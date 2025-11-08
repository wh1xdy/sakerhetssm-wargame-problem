default: tricky.py

tricky.py: generate.py
	python3 $< $@ "SSM{oh_no_my_sssecret_ssstasssh}"

test: tricky.py
	python3 $<

clean:
	rm -f tricky.py

.PHONY: default test clean
