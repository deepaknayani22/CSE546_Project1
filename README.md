CSE546 - Image Recognition as a Service

Team members

1. Karthik Aravapalli
   We have had numerous sessions to conceptualize how the workflow of our application would be and have had lengthy discussions about how to develop this application. I read a lot of tutorials, publications, and blogs about the various Amazon Services that we would utilize in this application, notably EC2, SQS, CloudWatch, and S3, after settling on the structure of our image detection program. My  main contribution to the project is that I'm in charge of designing and implementing the Web Tier.
In particular, I was in charge of comprehending the data flow from the Workload generator, which simulates a concurrent user's scenario of uploading inputs (images), and how the Web Tier will handle it. The Web Tier serves as the controller before pushing the requests into the request queue. The Web Tier is also in charge of showing users the results. At the Web Tier, two types of processing are carried out: pre-processing of the input image before it is added to the request queue and post-processing of the output following image recognition.

   
2. Deepak Reddy Nayani
   I took part in the brainstorming meetings that were held to determine the architecture to be used for our application. We determined which AWS services to use and how to connect them after reviewing various AWS resources.
My most significant contribution to this project was the design and implementation of the app-tier. The app-tier listens to the SQS queue and retrieves messages as soon as they are populated from the web-tier using EC2 instances. After that, the image is written to the S3 bucket before being sent to the Face recognition model for classification. The output result we obtain from the model is written back to the S3-output bucket for persistence. The result is then written to S3, and a message is then issued to the response queue.


3. Nikhil Chandra
   I was heavily involved with the auto-scaling architecture and AWS settings setup that was necessary for the project. In order to use the AWS services, my teammates and I worked together to create the necessary AWS IAM credentials. We have chosen to use EC2 for the application and web layers, SQS for the request message queue, and S3 buckets for input and output storage. I used AWS's Step-scaling policy to perform the autoscaling after looking into a number of alternatives.



