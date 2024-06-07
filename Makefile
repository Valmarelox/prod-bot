TF=terraform -chdir=terraform

.PHONY: deploy
deploy: release/.done

release/.done: release/terraform_result.json
	python3 scripts/update_bot.py $<
	@touch $@


release/terraform_result.json: release/terraform_result.json.tmp
	diff -q $< $@ || mv $< $@

release/terraform_result.json.tmp: release/*.zip $(shell find terraform -type f -name "*.zip" -or -name "*.tf" -or -name "*.tfvars")
	$(TF) apply -auto-approve
	$(TF) output -json > release/terraform_result.json.tmp

release/telegram-pocket-bot.zip: src/*.py
	@mkdir -p $(@D)
	cd src && zip -r ../$@ .

fmt: 
	$(TF) fmt
