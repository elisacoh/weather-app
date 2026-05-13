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


		
	}
}
