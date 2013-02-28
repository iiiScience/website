#! /bin/sh

java -jar compiler.jar \
	--js _jquery-1.*.js \
    --js _jquery.autocomplete.js \
	--js _results.js \
	--js _upload.js \
	--js _alertify.js \
	--js script.js > script.min.js