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
				withcredentials([usernamePassword(credentialsId: 'docker-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]){
					sh '''
						docker build -t $DOCKER_USER/weather-app:%BUILD_NUMBER .
						echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
						docker push $DOCKER_USER/weather-app:$BUILD_NUMBER
						cosign sign --yes $DOCKER_USER/weather-app:$BUILD_NUMBER
					'''
				echo '-------------------------------------- BUILD, PUSH, SIGN SUCCESSFULL --------------------------------------'
				}
			}
		}


		
	}
}
