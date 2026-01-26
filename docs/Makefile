html:
	asciidoctor --backend html5 --attribute data-uri --destination-dir output '**/*.adoc'
	if [ -d literature/assets ]; then cp -r literature/assets output/; fi

pdf:
	asciidoctor-pdf --require asciidoctor-mathematical -a pdf-theme=theme/tum.yml --destination-dir output '**/*.adoc'
