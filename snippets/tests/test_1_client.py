def test_instances():
    from subgatekit import SubgateClient, AsyncBaseClient

    client = SubgateClient(
        base_url='http://localhost:3000/api/v1',
        apikey='TEST_APIKEY_VALUE',
    )

    async_client = AsyncBaseClient(
        base_url='http://localhost:3000/api/v1',
        apikey='TEST_APIKEY_VALUE',
    )
