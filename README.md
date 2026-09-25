# GA4 Connector POC

A Python-based connector for extracting Google Analytics 4 (GA4)
reporting data through the Google Analytics Data API.

The current implementation focuses on understanding the complete
data flow from a GA4 API request to a standardized Python data
structure.

DuckDB storage will be added as a future stage.

---x

## Architecture

```text
                    CUSTOMER WEBSITE
                           │
                           │ GA4 Tracking
                           ▼
                    Google Analytics 4
                           │
                           │ Google Analytics Data API
                           ▼
                 ┌─────────────────────┐
                 │   GA4 Connector     │
                 │      (Python)       │
                 └──────────┬──────────┘
                            │
                            ▼
                  RunReportRequest
                            │
                  ┌─────────┴─────────┐
                  │                   │
             Dimensions            Metrics
                  │                   │
             eventName           eventCount
                  │                   │
                  └─────────┬─────────┘
                            │
                            ▼
                    Google GA4 API
                            │
                            ▼
                  RunReportResponse
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
        Dimension      Metric          Rows
         Headers       Headers
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                 Protobuf Values
                            │
                            ▼
                 Python Dictionaries
                            │
                            ▼
                  Standardized Records
                            │
                            ▼
                       DuckDB
                  (Future Stage)
                            │
                            ▼
                    Resulticks CDP
                  (Future Stage)