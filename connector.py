import os
import logging
from typing import Any

from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.api_core.exceptions import GoogleAPIError
from google.auth.exceptions import DefaultCredentialsError


# ============================================================
# CONFIGURATION
# ============================================================

PROPERTY_ID = "555643982"

load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS"
)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# GOOGLE CREDENTIALS
# ============================================================

if GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
        GOOGLE_APPLICATION_CREDENTIALS
    )

    logger.info("Google credentials configured")

else:
    logger.error(
        "GOOGLE_APPLICATION_CREDENTIALS is not configured"
    )


# ============================================================
# CREATE GA4 CLIENT
# ============================================================

def create_client() -> BetaAnalyticsDataClient:
    """
    Create a GA4 Data API client.
    """

    logger.info("Creating GA4 Data API client")

    return BetaAnalyticsDataClient()


# ============================================================
# GENERIC GA4 REPORT
# ============================================================

def run_report(
    client: BetaAnalyticsDataClient,
    dimensions: list[str],
    metrics: list[str],
    start_date: str = "7daysAgo",
    end_date: str = "today",
):
    """
    Execute a GA4 Data API report.

    This function shows:

    1. What we are requesting
    2. The RunReportRequest structure
    3. What GA4 returns
    4. The response headers and rows
    """

    # ========================================================
    # 1. LOG WHAT WE ARE REQUESTING
    # ========================================================

    print("\n")
    print("=" * 80)
    print("GA4 REPORT REQUEST")
    print("=" * 80)

    print(f"Property ID : {PROPERTY_ID}")
    print(f"Property    : properties/{PROPERTY_ID}")
    print(f"Dimensions  : {dimensions}")
    print(f"Metrics     : {metrics}")
    print(f"Date Range  : {start_date} -> {end_date}")

    print("=" * 80)

    logger.info(
        "Preparing GA4 RunReportRequest"
    )

    logger.info(
        "Property  : properties/%s",
        PROPERTY_ID,
    )

    logger.info(
        "Dimensions: %s",
        dimensions,
    )

    logger.info(
        "Metrics   : %s",
        metrics,
    )

    logger.info(
        "Date range: %s -> %s",
        start_date,
        end_date,
    )


    # ========================================================
    # 2. BUILD GA4 REQUEST
    # ========================================================

    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",

        dimensions=[
            Dimension(name=dimension)
            for dimension in dimensions
        ],

        metrics=[
            Metric(name=metric)
            for metric in metrics
        ],

        date_ranges=[
            DateRange(
                start_date=start_date,
                end_date=end_date,
            )
        ],
    )


    # ========================================================
    # 3. SHOW THE REQUEST STRUCTURE
    # ========================================================

    print("\n")
    print("-" * 80)
    print("REQUEST OBJECT SENT TO GA4")
    print("-" * 80)

    print(request)

    print("-" * 80)


    # ========================================================
    # 4. CALL GA4 API
    # ========================================================

    logger.info("Sending RunReportRequest to GA4 Data API...")

    response = client.run_report(request)


    # ========================================================
    # 5. BASIC RESPONSE INFORMATION
    # ========================================================

    print("\n")
    print("=" * 80)
    print("GA4 RESPONSE")
    print("=" * 80)

    print(
        f"Response type : {type(response)}"
    )

    print(
        f"Row count     : {len(response.rows)}"
    )

    print("=" * 80)


    # ========================================================
    # 6. RESPONSE HEADERS
    # ========================================================

    print("\n")
    print("-" * 80)
    print("RESPONSE DIMENSION HEADERS")
    print("-" * 80)

    for index, header in enumerate(
        response.dimension_headers
    ):
        print(
            f"[{index}] {header.name}"
        )


    print("\n")
    print("-" * 80)
    print("RESPONSE METRIC HEADERS")
    print("-" * 80)

    for index, header in enumerate(
        response.metric_headers
    ):
        print(
            f"[{index}] {header.name}"
            f" | type={header.type_}"
        )


    # ========================================================
    # 7. SHOW RAW ROW STRUCTURE
    # ========================================================

    print("\n")
    print("=" * 80)
    print("RAW RESPONSE ROWS")
    print("=" * 80)

    if not response.rows:

        print("No rows returned.")

    else:

        for row_index, row in enumerate(
            response.rows
        ):

            print(
                f"\nROW {row_index + 1}"
            )

            print(
                "Dimension values:"
            )

            for index, value in enumerate(
                row.dimension_values
            ):
                print(
                    f"  [{index}] {value.value}"
                )

            print(
                "Metric values:"
            )

            for index, value in enumerate(
                row.metric_values
            ):
                print(
                    f"  [{index}] {value.value}"
                )


    print("\n")
    print("=" * 80)
    print("END OF GA4 RESPONSE")
    print("=" * 80)


    logger.info(
        "GA4 report completed | rows=%d",
        len(response.rows),
    )

    return response


# ============================================================
# EXTRACT GA4 RESPONSE
# ============================================================

def extract_records(
    response,
) -> list[dict[str, Any]]:
    """
    Convert the GA4 API response into Python dictionaries.

    GA4 structure:

        dimension_headers
        metric_headers
        rows
            ├── dimension_values
            └── metric_values

    We use the headers to map each value
    to the correct field name.
    """

    print("\n")
    print("=" * 80)
    print("TRANSFORMING GA4 RESPONSE -> PYTHON DICTIONARIES")
    print("=" * 80)


    # ========================================================
    # 1. GET DIMENSION HEADER NAMES
    # ========================================================

    dimension_headers = [
        header.name
        for header in response.dimension_headers
    ]

    print(
        f"Dimension headers: {dimension_headers}"
    )


    # ========================================================
    # 2. GET METRIC HEADER NAMES
    # ========================================================

    metric_headers = [
        header.name
        for header in response.metric_headers
    ]

    print(
        f"Metric headers   : {metric_headers}"
    )


    # ========================================================
    # 3. PROCESS EVERY ROW
    # ========================================================

    records = []

    for row_index, row in enumerate(
        response.rows
    ):

        print("\n")
        print(
            f"Processing GA4 row #{row_index + 1}"
        )

        record = {}


        # ----------------------------------------------------
        # DIMENSIONS
        # ----------------------------------------------------

        print("  Dimensions:")

        for index, dimension_value in enumerate(
            row.dimension_values
        ):

            dimension_name = (
                dimension_headers[index]
            )

            dimension_value_text = (
                dimension_value.value
            )

            print(
                f"    {dimension_name}"
                f" = {dimension_value_text}"
            )

            record[dimension_name] = (
                dimension_value_text
            )


        # ----------------------------------------------------
        # METRICS
        # ----------------------------------------------------

        print("  Metrics:")

        for index, metric_value in enumerate(
            row.metric_values
        ):

            metric_name = (
                metric_headers[index]
            )

            metric_value_text = (
                metric_value.value
            )

            print(
                f"    {metric_name}"
                f" = {metric_value_text}"
            )

            record[metric_name] = (
                metric_value_text
            )


        # ----------------------------------------------------
        # FINAL PYTHON DICTIONARY
        # ----------------------------------------------------

        records.append(record)

        print(
            f"  -> Python record: {record}"
        )


    # ========================================================
    # 4. FINAL RESULT
    # ========================================================

    print("\n")
    print("-" * 80)
    print("EXTRACTED PYTHON RECORDS")
    print("-" * 80)

    for index, record in enumerate(records):

        print(
            f"{index + 1}. {record}"
        )


    print("-" * 80)

    logger.info(
        "GA4 records extracted | count=%d",
        len(records),
    )

    return records


# ============================================================
# EVENT / ACTIVITY DATA
# ============================================================

def get_event_data(
    client: BetaAnalyticsDataClient,
) -> list[dict[str, Any]]:

    """
    Get GA4 event/activity summary.
    """

    print("\n")
    print("#" * 80)
    print("EXTRACTING EVENT DATA")
    print("#" * 80)

    response = run_report(
        client=client,

        dimensions=[
            "eventName",
        ],

        metrics=[
            "eventCount",
        ],
    )

    return extract_records(response)


# ============================================================
# DAILY USER / BUSINESS DATA
# ============================================================

def get_daily_data(
    client: BetaAnalyticsDataClient,
) -> list[dict[str, Any]]:

    """
    Get daily GA4 user and business metrics.
    """

    print("\n")
    print("#" * 80)
    print("EXTRACTING DAILY DATA")
    print("#" * 80)

    response = run_report(
        client=client,

        dimensions=[
            "date",
        ],

        metrics=[
            "activeUsers",
            "newUsers",
            "sessions",
            "totalRevenue",
        ],
    )

    return extract_records(response)


# ============================================================
# STANDARDIZE EVENT DATA
# ============================================================

def standardize_event_records(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    """
    Convert GA4 event records into the structure
    that will eventually be stored in DuckDB.
    """

    print("\n")
    print("=" * 80)
    print("STANDARDIZING EVENT RECORDS")
    print("=" * 80)

    standardized_records = []

    for record in records:

        standardized_record = {
            "source": "google_analytics",

            "event_name": record.get(
                "eventName"
            ),

            "event_count": int(
                record.get(
                    "eventCount",
                    0,
                )
            ),

            "customer_id": None,

            "product_id": None,

            "transaction_id": None,

            "identity_status": "unresolved",
        }

        print(
            f"RAW         : {record}"
        )

        print(
            f"STANDARDIZED: {standardized_record}"
        )

        standardized_records.append(
            standardized_record
        )

    return standardized_records


# ============================================================
# STANDARDIZE DAILY DATA
# ============================================================

def standardize_daily_records(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    """
    Convert daily GA4 metrics into the standardized
    structure that will eventually be stored in DuckDB.
    """

    print("\n")
    print("=" * 80)
    print("STANDARDIZING DAILY RECORDS")
    print("=" * 80)

    standardized_records = []

    for record in records:

        standardized_record = {
            "source": "google_analytics",

            "date": record.get(
                "date"
            ),

            "active_users": int(
                record.get(
                    "activeUsers",
                    0,
                )
            ),

            "new_users": int(
                record.get(
                    "newUsers",
                    0,
                )
            ),

            "sessions": int(
                record.get(
                    "sessions",
                    0,
                )
            ),

            "total_revenue": float(
                record.get(
                    "totalRevenue",
                    0,
                )
            ),
        }

        print(
            f"RAW         : {record}"
        )

        print(
            f"STANDARDIZED: {standardized_record}"
        )

        standardized_records.append(
            standardized_record
        )

    return standardized_records


# ============================================================
# PRINT STANDARDIZED DATA
# ============================================================

def print_standardized_data(
    event_records: list[dict[str, Any]],
    daily_records: list[dict[str, Any]],
):

    print("\n")
    print("=" * 80)
    print("STANDARDIZED DATA - READY FOR DUCKDB")
    print("=" * 80)

    print("\n[ACTIVITY RECORDS]")
    print("-" * 80)

    if event_records:

        for record in event_records:
            print(record)

    else:
        print("No activity records found.")


    print("\n[DAILY AGGREGATE RECORDS]")
    print("-" * 80)

    if daily_records:

        for record in daily_records:
            print(record)

    else:
        print("No daily records found.")


    print("\n")
    print("=" * 80)
    print("END OF STANDARDIZED DATA")
    print("=" * 80)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        # ----------------------------------------------------
        # 1. Create GA4 client
        # ----------------------------------------------------

        client = create_client()


        # ----------------------------------------------------
        # 2. Extract data from GA4
        # ----------------------------------------------------

        raw_event_records = get_event_data(
            client
        )

        raw_daily_records = get_daily_data(
            client
        )


        # ----------------------------------------------------
        # 3. Standardize data
        # ----------------------------------------------------

        event_records = standardize_event_records(
            raw_event_records
        )

        daily_records = standardize_daily_records(
            raw_daily_records
        )


        # ----------------------------------------------------
        # 4. Print final data
        # ----------------------------------------------------

        print_standardized_data(
            event_records,
            daily_records,
        )


        # ----------------------------------------------------
        # 5. Summary
        # ----------------------------------------------------

        print("\nExtraction summary:")

        print(
            f"Activity records : {len(event_records)}"
        )

        print(
            f"Daily records    : {len(daily_records)}"
        )

        print(
            "\nConnector completed successfully."
        )


    except (
        DefaultCredentialsError,
        GoogleAPIError,
    ) as error:

        logger.exception(
            "GA4 connector failed"
        )

        print(
            f"\nGA4 connector failed: {error}"
        )