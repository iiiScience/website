#! /bin/sh

java -jar compiler.jar \
	--js _jquery*.js \
	--js _results.js \
	--js _upload.js \
	--js script.js > script.min.js