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
		
	}
}
