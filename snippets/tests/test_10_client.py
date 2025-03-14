def test_instances():
    from subgatekit import SubgateClient, AsyncSubgateClient

    client = SubgateClient(
        base_url='http://localhost:3000/api/v1',
        apikey_public_id='TEST_APIKEY_PUBLIC_ID',
        apikey_secret='TEST_APIKEY_VALUE',
    )

    async_client = AsyncSubgateClient(
        base_url='http://localhost:3000/api/v1',
        apikey_public_id='TEST_APIKEY_PUBLIC_ID',
        apikey_secret='TEST_APIKEY_VALUE',
    )
