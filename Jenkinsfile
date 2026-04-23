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
            image: alpine/k8s:1.32.0
            command:
            - sleep
            args:
            - "9999999"
            env:
            - name: KUBECONFIG
              value: /tmp/kube/config
            volumeMounts:
            - name: kubeconfig
              mountPath: /tmp/kube
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
    GITLAB_TOKEN = credentials('gitlab-token')
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

stage('Update Helm values - dev') {
      when { branch 'dev' }
      steps {
        container('kubectl') {
          sh """
            git config --global user.email "jenkins@devops-elisa.space"
            git config --global user.name "Jenkins"
            git clone http://root:${GITLAB_TOKEN}@10.0.3.20/root/weather-app-helm.git
            cd weather-app-helm
            sed -i "s|tag:.*|tag: \\"${SHORT_SHA}\\"|g" values.yaml
            git add values.yaml
            git commit -m "ci: update dev image to ${SHORT_SHA}"
            git push origin main
          """
        }
      }
    }

    stage('Update Helm values - staging') {
      when { branch 'staging' }
      steps {
        container('kubectl') {
          sh """
            git config --global user.email "jenkins@devops-elisa.space"
            git config --global user.name "Jenkins"
            git clone http://root:${GITLAB_TOKEN}@10.0.3.20/root/weather-app-helm.git
            cd weather-app-helm
            sed -i "s|tag:.*|tag: \\"${SHORT_SHA}\\"|g" values.yaml
            git add values.yaml
            git commit -m "ci: update staging image to ${SHORT_SHA}"
            git push origin main
          """
        }
      }
    }

    stage('Update Helm values - production') {
      when { branch 'main' }
      steps {
        container('kubectl') {
          sh """
            git config --global user.email "jenkins@devops-elisa.space"
            git config --global user.name "Jenkins"
            git clone http://root:${GITLAB_TOKEN}@10.0.3.20/root/weather-app-helm.git
            cd weather-app-helm
            sed -i "s|tag:.*|tag: \\"${SHORT_SHA}\\"|g" values-production.yaml
            git add values.yaml
            git commit -m "ci: update production image to ${SHORT_SHA}"
            git push origin main
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
