# SPRT::ApiGateway::Deployment

This resource type enables blue/green deployments with canaries and automatic tests via CloudFormation. The resource
provider will generate two stages in given REST API of the API Gateway called _blue_ and _green_. If you create a
deployment in the same template this deployment will be released to both stages.  
Upon update, you can execute a given AWS StepFunction that runs tests against the green stage of your API and you can
configure canary percentages. Canaries will receive traffic for 15 minutes on the blue stage. After that, the change
will be promoted completely. Use CloudWatch alarms and CloudFormation rollback triggers to handle errors on Canaries. 


## How to use
Deploy this resource with `cfn submit`


## Example
`example/infrastructure.yaml` is a template that demonstrates how to use this resource. It contains a simple
"Hello World" That is invoked via API Gateway. A test lambda verifies this at the API with a simple http request. If 
you want to deploy changes, change the logical ID of the lambda function version and the deployment to force a
replacement. This should usually be automated, like SAM does it for Lambda versions or via CDK.