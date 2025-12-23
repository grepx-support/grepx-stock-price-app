# price_app/src/main/prefect_app/deployments/deploy_price_flows.py

from price_app.src.main.prefect_app.flows.etl_price_flow import price_etl_flow


if __name__ == "__main__":
    price_etl_flow.from_source(
        source=".",  # repo root: d:\GrepX\newpriceapp\grepx-orchestrator
        entrypoint="price_app/src/main/prefect_app/flows/etl_price_flow.py:price_etl_flow",
    ).deploy(
        name="price-etl",
        work_pool_name="price-pool",
        tags=["price", "etl", "prefect"],
    )
    
    print("Successfully deployed price_etl_flow")