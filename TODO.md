# TODO

## Features

- Add loading overlay when options changed (faded out and spinner)
- Map to check/uncheck states in time graph
- Some way to make the data auto-refresh?
- Add a data smoothing option (average change/doubling rate over multiple days)

## Fix

- Make the map have a default state, instead of the empty graph look (might be fixed by adding loading overlay)
- Make it responsive/mobile-friendly
- Refactor to avoid repeated re-computation (especially with multi-day averaging)
- If it's a county's first day, the change from the previous day is NaN and it doesn't render in the hovertemplate (it's left as the `%{customdata[#]}`).