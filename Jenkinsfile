pipeline {
  agent {
    kubernetes {
      namespace 'default'
      yaml """
        apiVersion: v1
        kind: Pod
        spec:
          containers:
          - name: jnlp
            image: jenkins/inbound-agent:latest
          - name: kaniko
            image: gcr.io/kaniko-project/executor:debug
            command:
            - sleep
            args:
            - "9999999"
            volumeMounts:
            - name: kaniko-secret
              mountPath: /kaniko/.docker
          - name: python
            image: python:3.12-slim
            command:
            - sleep
            args:
            - "9999999"
          - name: kubectl
            image: bitnami/kubectl:latest
            command:
            - sleep
            args:
            - "9999999"
            volumeMounts:
            - name: kubeconfig
              mountPath: /root/.kube
          volumes:
          - name: kaniko-secret
            secret:
              secretName: ecr-secret
              items:
              - key: .dockerconfigjson
                path: config.json
          - name: kubeconfig
            secret:
              secretName: kubeconfig-secret
              items:
              - key: config
                path: config
      """
    }
  }

  environment {
    ECR_REPO     = "275115135718.dkr.ecr.eu-west-1.amazonaws.com/weather-app-infra-weather-app"
    AWS_REGION   = "eu-west-1"
    CLUSTER_NAME = "weather-app-infra-cluster"
  }

  stages {
    stage('Info') {
      steps {
        script {
          env.SHORT_SHA = env.GIT_COMMIT.take(7)
        }
        sh 'echo "Branch: ${BRANCH_NAME}"'
        sh 'echo "SHA: ${SHORT_SHA}"'
      }
    }

    stage('Lint & Test') {
      steps {
        container('python') {
          sh '''
            pip install --quiet -r requirements.txt pylint
            pylint --fail-under=7.0 *.py
          '''
        }
      }
    }

    stage('Build & Push') {
      when {
        anyOf {
          branch 'dev'
          branch 'staging'
        }
      }
      steps {
        container('kaniko') {
          sh """
            /kaniko/executor \\
              --context=. \\
              --dockerfile=Dockerfile.multistage \\
              --destination=${ECR_REPO}:${SHORT_SHA} \\
              --destination=${ECR_REPO}:${BRANCH_NAME}-latest
          """
        }
      }
    }

    stage('Deploy to dev') {
      when { branch 'dev' }
      steps {
        container('kubectl') {
          sh """
            sed -i "s|IMAGE_PLACEHOLDER|${ECR_REPO}:${SHORT_SHA}|g" k8s/deployment.yaml
            sed -i "s|NAMESPACE_PLACEHOLDER|dev|g" k8s/deployment.yaml k8s/service.yaml k8s/ingress.yaml
            sed -i "s|CERT_ARN_PLACEHOLDER|arn:aws:acm:eu-west-1:275115135718:certificate/603b1797-5e02-4075-8108-db2d0eb51869|g" k8s/ingress.yaml
            kubectl apply -f k8s/
          """
        }
      }
    }

    stage('Deploy to staging') {
      when { branch 'staging' }
      steps {
        container('kubectl') {
          sh """
            sed -i "s|IMAGE_PLACEHOLDER|${ECR_REPO}:${SHORT_SHA}|g" k8s/deployment.yaml
            sed -i "s|NAMESPACE_PLACEHOLDER|staging|g" k8s/deployment.yaml k8s/service.yaml k8s/ingress.yaml
            sed -i "s|CERT_ARN_PLACEHOLDER|arn:aws:acm:eu-west-1:275115135718:certificate/603b1797-5e02-4075-8108-db2d0eb51869|g" k8s/ingress.yaml
            kubectl apply -f k8s/
          """
        }
      }
    }

    stage('Deploy to production') {
      when { branch 'main' }
      steps {
        container('kubectl') {
          sh """
            sed -i "s|IMAGE_PLACEHOLDER|${ECR_REPO}:${SHORT_SHA}|g" k8s/deployment.yaml
            sed -i "s|NAMESPACE_PLACEHOLDER|production|g" k8s/deployment.yaml k8s/service.yaml k8s/ingress.yaml
            sed -i "s|CERT_ARN_PLACEHOLDER|arn:aws:acm:eu-west-1:275115135718:certificate/603b1797-5e02-4075-8108-db2d0eb51869|g" k8s/ingress.yaml
            kubectl apply -f k8s/
            kubectl rollout status deployment/flask-app -n production --timeout=120s || \\
              kubectl rollout undo deployment/flask-app -n production
          """
        }
      }
    }
  }

	post {
	    success {
	      echo "Pipeline succeeded - ${env.BRANCH_NAME}:${env.GIT_COMMIT?.take(7)}"
	    }
	    failure {
	      echo "Pipeline failed - ${env.BRANCH_NAME}:${env.GIT_COMMIT?.take(7)}"
	    }
  }
}
