html:
	asciidoctor --backend html5 --attribute data-uri --destination-dir output '**/*.adoc'
	cp -r literature/assets output/

pdf:
	asciidoctor-pdf --require asciidoctor-mathematical -a pdf-theme=theme/tum.yml --destination-dir output '**/*.adoc'
