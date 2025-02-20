def test_instances():
    from subgatekit import SubgateClient

    client = SubgateClient(
        base_url='http://localhost:3000/api/v1',
        apikey='TEST_APIKEY_VALUE',
    )

