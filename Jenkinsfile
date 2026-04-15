pipeline {
  agent {label 'docker' }

  environment{
    IMAGE = "elcosah/weather-app"
  }

  stages{
    stage('INFO')
    {
      steps{
        script {
        env.TAG = env.GIT_COMMIT.take(7)
        }

        sh 'echo "$GIT_COMMIT"'   
        sh 'echo "TAG=$TAG"'
        sh 'echo "IMAGE=$IMAGE"'
        }
    }
    stage('STATIC TESTS')
    {
      steps{
        echo "Static Tests Starting... - pylint in Docker"
        sh '''
        #!/usr/bin/env bash
        set -eux
        docker --version

        docker run --rm \
          -v "$PWD:/app" -w /app \
          python:3.12-slim \
          bash -lc '
            python --version &&
            pip install --upgrade pip &&
            if [ -f requirements.txt ]; then pip install -r requirements.txt; fi &&
            pip install pylint &&
            pylint --fail-under=7.0 $(ls *.py)
            '
        '''
      }
    }

    stage('BUILD'){
      steps{
        echo "Build Docker  image"
        sh '''
          set -eux
          docker build -f Dockerfile.multistage -t "$IMAGE:$TAG" .
        '''
      }
    }

stage('Smoke Test') {
  steps {
    echo "Smoke test: container starts and responds"
    sh '''
      set -eux

      # Cleanup if previous run left something
      docker rm -f weather-smoke 2>/dev/null || true

      # Run container from the freshly built image
      docker run -d --name weather-smoke -p 8080:5000 "$IMAGE:$TAG"

      # Optional: show logs in case it fails later
      docker ps --filter name=weather-smoke

      # Wait/retry for the service to become reachable
      for i in 1 2 3 4 5; do
        if curl -fsS "http://localhost:8080/" >/dev/null; then
          echo "Smoke test OK"
          break
        fi
        echo "Waiting for app... ($i)"
        sleep 2
      done

      # Final check (fail pipeline if still not responding)
      curl -fsS "http://localhost:8080/" >/dev/null

      # Cleanup container
      docker rm -f weather-smoke
    '''
    }
  }

stage('DEBUG BRANCH') {
  steps {
    sh '''
      set -e
      echo "BRANCH_NAME=${BRANCH_NAME:-<unset>}"
      echo "GIT_BRANCH=${GIT_BRANCH:-<unset>}"
      git rev-parse --abbrev-ref HEAD || true
      git branch -avv || true
    '''
  }
}


  stage('PUSH') {
    when {
      expression { return (env.GIT_BRANCH ?: '') == 'origin/main' }
    }
    steps {
      echo "Push validated image to Docker Hub"
      withCredentials([usernamePassword(credentialsId: 'docker-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
        sh '''
          set -eux
          echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin

          docker push "$IMAGE:$TAG"

          docker tag "$IMAGE:$TAG" "$IMAGE:latest"
          docker push "$IMAGE:latest"

          docker logout
        '''
      }
    }
  }



  stage('DEPLOY') {
    when {
      expression { (env.GIT_BRANCH ?: '') == 'origin/main' }
    }
    steps {
      echo "Deploy $IMAGE:$TAG to production"

      withCredentials([sshUserPrivateKey(credentialsId: 'prod-ssh', keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')]) {
        sh '''
          set -eux

          ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@13.61.183.159" "
            set -eux
            docker pull $IMAGE:$TAG
            docker rm -f weather-app 2>/dev/null || true
            docker run -d --name weather-app -p 80:5000 $IMAGE:$TAG
            sleep 2
            curl -fsS http://localhost/ >/dev/null
          "
        '''
      }
    }
  }


  }
}



