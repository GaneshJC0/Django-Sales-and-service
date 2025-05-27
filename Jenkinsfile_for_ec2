pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1'
        AMI_ID = 'ami-0abcdef1234567890' // Replace with a real Ubuntu AMI
        INSTANCE_TYPE = 't2.micro'
        KEY_NAME = 'your-key-name' // Must already exist in AWS
        SECURITY_GROUP_ID = 'sg-xxxxxxxx' // Your security group
        SUBNET_ID = 'subnet-xxxxxxxx' // Your subnet
        SSH_CREDENTIALS_ID = 'ec2-ssh-key'
        GIT_REPO = 'https://github.com/your-username/your-repo.git'
    }

    stages {
        stage('Launch EC2 Instance') {
            steps {
                script {
                    def launchCommand = """
                        aws ec2 run-instances \
                          --image-id ${AMI_ID} \
                          --count 1 \
                          --instance-type ${INSTANCE_TYPE} \
                          --key-name ${KEY_NAME} \
                          --security-group-ids ${SECURITY_GROUP_ID} \
                          --subnet-id ${SUBNET_ID} \
                          --region ${AWS_REGION} \
                          --query 'Instances[0].InstanceId' \
                          --output text
                    """

                    def instanceId = sh(script: launchCommand, returnStdout: true).trim()
                    echo "Launched EC2 Instance: ${instanceId}"

                    // Wait for the instance to be in 'running' state
                    sh """
                        aws ec2 wait instance-running --instance-ids ${instanceId} --region ${AWS_REGION}
                    """

                    // Get public IP
                    def publicIp = sh(
                        script: "aws ec2 describe-instances --instance-ids ${instanceId} --region ${AWS_REGION} --query 'Reservations[0].Instances[0].PublicIpAddress' --output text",
                        returnStdout: true
                    ).trim()

                    echo "Instance Public IP: ${publicIp}"

                    // Store IP for later use
                    writeFile file: 'ec2_ip.txt', text: publicIp
                }
            }
        }

        stage('Remote Setup on EC2') {
            steps {
                script {
                    def publicIp = readFile('ec2_ip.txt').trim()

                    sshagent([SSH_CREDENTIALS_ID]) {
                        sh """
                            ssh -o StrictHostKeyChecking=no ubuntu@${publicIp} << 'ENDSSH'
                                sudo apt update && sudo apt upgrade -y
                                sudo apt install -y python3 python3-venv python3-pip git
                                mkdir -p ~/project
                                cd ~/project
                                python3 -m venv venv
                                source venv/bin/activate
                                git clone ${GIT_REPO}
                                cd $(basename ${GIT_REPO} .git)
                                if [ -f requirements.txt ]; then
                                    pip install -r requirements.txt
                                fi
                            ENDSSH
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo '✅ EC2 created and setup completed!'
        }
        failure {
            echo '❌ Something went wrong.'
        }
    }
}
