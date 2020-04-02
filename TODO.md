# TODO

## Features

- Add loading overlay when options changed (faded out and spinner)
  - See [Loading states API and a Loading component prerelease](https://community.plotly.com/t/loading-states-api-and-a-loading-component-prerelease/16406) and [Dash loading states](https://community.plotly.com/t/dash-loading-states/5687)
- Map to check/uncheck states in time graph
- Some way to make the data auto-refresh?
- Add a data smoothing option (average change/doubling rate over multiple days)

## Fix

- Make the map have a default state, instead of the empty graph look (might be fixed by adding loading overlay)
- Make it responsive/mobile-friendly
- Refactor to avoid repeated re-computation (especially with multi-day averaging)