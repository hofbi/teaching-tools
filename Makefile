file_finder = find . -type f \( $(1) \) -not \( -path '*/venv/*' -o -path '*/build/*' -o -path '*/cmake-build-debug/*' -o -path '*/workspace/*' \)

SLIDE_FILES = $(call file_finder,-name slide-deck.md)
SLIDE_FILES_LIGHT = $(call file_finder,-name slide-deck-light.md)

.PHONY: test
test:
	cd tools && python3 -m unittest discover

coverage:
	cd tools && coverage run --source=. -m unittest discover
	cd tools && coverage report -m

coverage_reports: coverage
	cd tools && coverage xml
	sed -i -e 's, filename=", filename="tools/,g' tools/coverage.xml
	cd tools && coverage html

.PHONY: slides
slides: light_theme_slides
	cd slides && mkdir -p build && cp -r lecture/images build/
	cd slides && docker compose run generate --input-dir ./lecture
	cd slides && docker compose run generate --input-dir ./lecture --pdf
	cd slides && docker compose run generate --input-dir ./homework
	cd slides && docker compose run generate --input-dir ./homework --pdf

serve: light_theme_slides
	cd slides && docker compose up

.PHONY: docs
docs:
	cd docs && docker compose run html
	cd docs && docker compose run pdf

light_theme_slides:
	$(SLIDE_FILES) | xargs -I '{}' sh -c 'v={}; cp $$v $${v%.md}-light.md'
	$(SLIDE_FILES_LIGHT) | xargs sed -i '/class. invert/d'
	$(SLIDE_FILES_LIGHT) | xargs sed -i '/- invert/d'

clean_workspace:
	rm -rf workspace

clean_export:
	rm -rf export

package: clean_export
	$(call export_runner,source/example,example)

solution_package: clean_export
	$(call export_runner,source/example -k,example)
