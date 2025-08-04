file_finder = find . -type f \( $(1) \) -not \( -path '*/venv/*' -o -path '*/build/*' -o -path '*/cmake-build-debug/*' -o -path '*/workspace/*' \)

export_runner = python3 tools/export_files.py $(1) -o export/$(2) && cd export && zip -r $(2).zip $(2)

SLIDE_FILES = $(call file_finder,-name slide-deck.md)
SLIDE_FILES_LIGHT = $(call file_finder,-name slide-deck-light.md)

.PHONY: test
test:
	pytest tools

coverage:
	pytest --cov=tools --cov-config=tools/.coveragerc tools

coverage_reports:
	pytest --cov=tools --cov-config=tools/.coveragerc --cov-report=xml --cov-report=html tools

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

clean_export:
	rm -rf export

light_theme_slides:
	$(SLIDE_FILES) | xargs -I '{}' sh -c 'v={}; cp $$v $${v%.md}-light.md'
	$(SLIDE_FILES_LIGHT) | xargs sed -i '/class. invert/d'
	$(SLIDE_FILES_LIGHT) | xargs sed -i '/- invert/d'

clean_workspace:
	rm -rf workspace

package: clean_export
	$(call export_runner,source/example,example)

solution_package: clean_export
	$(call export_runner,source/example -k,example_solution)
