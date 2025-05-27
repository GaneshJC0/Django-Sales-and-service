pipeline {
  agent any

  environment {
    DOCKERHUB_USERNAME = 'ganeshjchoudhary'
    DOCKERHUB_REPOSITORY = 'django-ecommerce'
    IMAGE_TAG = 'latest'
    DOCKERHUB_CREDENTIALS_ID = 'dockerhub-credentials'
    KUBECONFIG_CREDENTIALS_ID = 'kubeconfig'
    K8S_NAMESPACE = 'django-app'
  }

  stages {
    stage('Checkout Code') {
      steps {
        git credentialsId: 'github-token',
            url: 'https://github.com/GaneshJC0/Django-Sales-and-service.git',
            branch: 'main'
      }
    }

    stage('Generate and Apply .env.prod Secret') {
      steps {
        withCredentials([
          string(credentialsId: 'DJANGO_SECRET_KEY', variable: 'DJANGO_SECRET_KEY'),
          string(credentialsId: 'RAZORPAY_KEY_ID', variable: 'RAZORPAY_KEY_ID'),
          string(credentialsId: 'RAZORPAY_KEY_SECRET', variable: 'RAZORPAY_KEY_SECRET'),
          string(credentialsId: 'DB_NAME', variable: 'DB_NAME'),
          string(credentialsId: 'DB_USER', variable: 'DB_USER'),
          string(credentialsId: 'DB_PASSWORD', variable: 'DB_PASSWORD'),
          string(credentialsId: 'DB_HOST', variable: 'DB_HOST')
        ]) {
          withKubeConfig(credentialsId: env.KUBECONFIG_CREDENTIALS_ID) {
            sh '''
              # Ensure namespace exists
              kubectl get ns ${K8S_NAMESPACE} || kubectl create ns ${K8S_NAMESPACE}

              # Create .env.prod file with sensitive vars from environment
              cat <<EOF > .env.prod
              DEBUG=False
              SECRET_KEY=$DJANGO_SECRET_KEY
              RAZORPAY_KEY_ID=$RAZORPAY_KEY_ID
              RAZORPAY_KEY_SECRET=$RAZORPAY_KEY_SECRET
              DB_NAME=$DB_NAME
              DB_USER=$DB_USER
              DB_PASSWORD=$DB_PASSWORD
              DB_HOST=$DB_HOST
              DB_PORT=5432
              EOF

              # Recreate secret
              kubectl delete secret django-env-prod -n ${K8S_NAMESPACE} --ignore-not-found
              kubectl create secret generic django-env-prod --from-file=.env.prod -n ${K8S_NAMESPACE}
            '''
          }
        }
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        withKubeConfig(credentialsId: env.KUBECONFIG_CREDENTIALS_ID) {
          sh """
            sed 's|__IMAGE_TAG__|${IMAGE_TAG}|g' k8s/deployment.yaml | kubectl apply -n ${K8S_NAMESPACE} -f -
            kubectl set image deployment/django-app django-app=docker.io/${DOCKERHUB_USERNAME}/${DOCKERHUB_REPOSITORY}:${IMAGE_TAG} -n ${K8S_NAMESPACE}
          """
        }
      }
    }

    stage('Restart Deployment to Apply Secrets') {
      steps {
        withKubeConfig(credentialsId: env.KUBECONFIG_CREDENTIALS_ID) {
          sh "kubectl rollout restart deployment django-app -n ${K8S_NAMESPACE}"
        }
      }
    }

    stage('Verify Deployment') {
      steps {
        withKubeConfig(credentialsId: env.KUBECONFIG_CREDENTIALS_ID) {
          sh "kubectl rollout status deployment/django-app -n ${K8S_NAMESPACE}"
        }
      }
    }
  }
}
