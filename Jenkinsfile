pipeline {
	agent any

	stages {
		stage('Checkout'){
			steps {
				echo 'Code Checkout --> success'
			}
		}

		stage('Hello'){
			steps {
				echo 'pipeline is working'
				sh 'whoami'
				sh 'pwd'
			}
		}

		stage('Step 1 - Dependency Scan') {
			steps {
				echo '---------STARTING DEPENDENCIES SCAN--------------------'
				sh '''
					trivy fs --severity CRITICAL --exit-code 1 --scanners vuln requirements.txt
				'''
				echo '---------DEPENDENCIES SCAN SUCCESSFULL-----------------'
			}
		}

		stage('Step 2 - DOCKER FILE SCAN'){
			steps {
				echo '----------------- STARTING DOCKERFILE SCAN ----------------- '
				sh '''
					trivy config --severity HIGH,CRITICAL --exit-code 1 Dockerfile
				'''
				echo '----------------- DOCKERFILE SCAN SUCCESSFULL ----------------- '
			}
		}

		stage('Step 3 - STATIC CODE ANALYSIS ON MERGE') {
		    when {
		        not { branch 'main' }
		    }
		    steps {
		        echo '----------------- STARTING STATIC CODE ANALYSIS  ----------------- '
		        withSonarQubeEnv('sonarqube') {
                    withEnv(["PATH+SONAR=${tool 'sonarqube-scanner'}/bin"]) {
		            sh '''
	                   sonar-scanner -Dsonar.projectKey=weather-app -Dsonar.sources=.
		            '''
		            }
		        }
		        echo '----------------- STATIC CODE ANALYSIS SUCCESSFULL ----------------- '
		    }
		}

		stage('Step 4 - Build, Push & Sign'){
			steps {
				echo '----------------------------- STARTING BUILD, PUSH & SIGN --------------------------'
				withCredentials([
					usernamePassword(credentialsId: 'docker-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS'),
					file(credentialsId: 'cosign-key', variable: 'COSIGN_KEY'),
					string(credentialsId: 'cosign-password', variable: 'COSIGN_PASSWORD')
				])
				{
					sh '''
						docker build -t $DOCKER_USER/weather-app:$BUILD_NUMBER .
						echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
					    DIGEST=$(docker push $DOCKER_USER/weather-app:$BUILD_NUMBER | grep digest | awk '{print $3}')
						cosign sign --yes --key $COSIGN_KEY $DOCKER_USER/weather-app@$DIGEST
   						
						
						# docker push $DOCKER_USER/weather-app:$BUILD_NUMBER
						# cosign sign --yes $DOCKER_USER/weather-app:$BUILD_NUMBER
					'''
				echo '-------------------------------------- BUILD, PUSH, SIGN SUCCESSFULL --------------------------------------'
				}
			}
		}

		stage('Step 5 - Verify & Deploy') {
		    steps {
		        echo '----------------- STARTING VERIFY & DEPLOY ----------------- '
		        withCredentials([usernamePassword(credentialsId: 'docker-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
		            sh '''
		                DIGEST=$(docker pull $DOCKER_USER/weather-app:$BUILD_NUMBER | grep Digest | awk '{print $2}')
		                cosign verify --key cosign.pub $DOCKER_USER/weather-app@$DIGEST
		                docker run -d --name weather-app -p 5000:5000 $DOCKER_USER/weather-app:$BUILD_NUMBER
		            '''
		        }
		        echo '----------------- VERIFY SUCCESSFULL - DEPLOYED ----------------- '
		    }
	    }
		
	}
}
