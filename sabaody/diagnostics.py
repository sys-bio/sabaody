from uuid import uuid4

def test_memcached(mc_host, mc_port):
    # test that memcache is working
    from pymemcache.client.base import Client
    mc_client = Client((mc_host,mc_port))
    my_id = str(uuid4())
    my_val = str(uuid4())
    mc_client.set(my_id, my_val, 1000)
    if mc_client.get(my_id).decode('utf8') != my_val:
        raise RuntimeError('Unable to communicate with Memcached')