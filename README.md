# Ecom_flask_backend_api
install dependency 
pip install -r requirements.txt


++++run project++++
python3 app.py

=======flask webapp deploy using ci/cd pipeline on jenkins follow steps are use to build declarative pipeline on aws ec2  =========
fully ci/cd_jenkins_declarative_pipeline_script
pipeline{
    agent any 
//1.clone code from github repository 
    stages{
        stage("clone code"){
            steps{
                echo "cloning the code "
                git url:"https://github.com/dimpal-0207/Ecom_flask_backend_api.git", branch: "master"
            }
        }
//2.build docker image from github repository 
        stage("build"){
             steps{
                echo "builing the code"
                sh "docker build -t flask_app ." 
            }
        }
//3. push docker image on docker diemon repository using global credential on jenkins  
        stage("Push to Docker hub"){
             steps {
                echo "Pushing the image into Docker Hub"
                withCredentials([usernamePassword(credentialsId: "dockerHub", passwordVariable: "dockerHubPass", usernameVariable: "dockerHubUser")]) {
                    sh "docker tag flask_app ${dockerHubUser}/flask_app:latest"
                    sh "docker login -u ${dockerHubUser} -p ${dockerHubPass}"
                    sh "docker push  ${dockerHubUser}/flask_app:latest" // Replace with your Docker image name
                }
            }
        }
//4.deploy on ec2 docker container 
        stage("Deploy"){
             steps{
                echo "deploying the container"
                sh "docker run -d -p 8000:8000 dimpal0207/flask_app:latest"
            }
        }
        
    }
}
    
