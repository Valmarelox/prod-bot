
output "api_url" {
  value = "${aws_apigatewayv2_stage.telegram-webhook-stage.invoke_url}telegram-pocket-bot"
}
output "bot_token" {
  value = var.bot_token
}

output "telegram_webhook_secret" {
  value = var.telegram_webhook_secret
}