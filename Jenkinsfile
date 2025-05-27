pipeline {
  agent any

  environment {
    DOCKERHUB_USERNAME = 'ganeshjchoudhary'
    DOCKERHUB_REPOSITORY = 'django-ecommerce'
    IMAGE_TAG = 'latest'  // or specific tag like '42'
    KUBECONFIG_CREDENTIALS_ID = 'kubeconfig'
    K8S_NAMESPACE = 'django-app'
  }

  stages {
    stage('Checkout Code') {
      steps {
        git credentialsId: 'github-token', url: 'https://github.com/YourUsername/django-app-repo.git', branch: 'main'
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        withKubeConfig(credentialsId: env.KUBECONFIG_CREDENTIALS_ID) {
          script {
            sh """
            kubectl get ns ${K8S_NAMESPACE} || kubectl create ns ${K8S_NAMESPACE}

            # Replace image tag dynamically in deployment YAML before apply
            sed 's|__IMAGE_TAG__|${IMAGE_TAG}|g' k8s/deployment.yaml | kubectl apply -n ${K8S_NAMESPACE} -f -

            # Ensure image gets updated even if deployment exists
            kubectl set image deployment/django-app django-app=docker.io/${DOCKERHUB_USERNAME}/${DOCKERHUB_REPOSITORY}:${IMAGE_TAG} -n ${K8S_NAMESPACE}
            """
          }
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
