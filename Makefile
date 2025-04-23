TF=terraform -chdir=terraform

.PHONY: deploy
deploy: release/.done

release/.done: release/terraform_result.json
	python3 scripts/update_bot.py $<
	@touch $@


release/terraform_result.json: release/terraform_result.json.tmp
	diff -q $< $@ || mv $< $@

release/terraform_result.json.tmp: release/telegram-pocket-bot.zip $(shell find terraform -type f -name "*.zip" -or -name "*.tf" -or -name "*.tfvars") .terraform_init
	$(TF) apply -auto-approve -var-file=local_secrets.tfvars
	$(TF) output -json > release/terraform_result.json.tmp

release/telegram-pocket-bot.zip: src/*.py
	@mkdir -p $(@D)
	cd src && zip -r ../$@ . -x "*.pyc" "*.pyo" "__pycache__/*" "*.zip" "*.tar.gz" "*.tgz" ".*" "*~"


.terraform_init:
	$(TF) init
	@touch $@

fmt: 
	$(TF) fmt
