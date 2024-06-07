
resource "aws_cloudwatch_event_rule" "morning-daily" {
  name                = "morning-daily"
  schedule_expression = "cron(30 3 * * ? *)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.morning-daily.name
  target_id = "telegram-pocket-bot"
  arn       = aws_lambda_function.telegrampocketbot.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.telegrampocketbot.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.morning-daily.arn
}


resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.telegrampocketbot.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.telegram-webhook.execution_arn}/*/*/telegram-pocket-bot"
}

resource "aws_apigatewayv2_api" "telegram-webhook" {
  name          = "telegram-webhook-endpoint"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "telegram_integration" {
  api_id                 = aws_apigatewayv2_api.telegram-webhook.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.telegrampocketbot.arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "telegram-webhook-route" {
  api_id    = aws_apigatewayv2_api.telegram-webhook.id
  route_key = "POST /telegram-pocket-bot"
  target    = "integrations/${aws_apigatewayv2_integration.telegram_integration.id}"
}

resource "aws_apigatewayv2_stage" "telegram-webhook-stage" {
  api_id      = aws_apigatewayv2_api.telegram-webhook.id
  name        = "$default"
  auto_deploy = true
}
