def test_complete_voting_flow(client, auth):
    candidate = client.post("/candidates", json={"name": "Ana Pérez", "party": "Partido A"}, headers=auth)
    assert candidate.status_code == 201
    voter = client.post("/voters", json={"name": "Luis Gómez", "email": "luis@example.com"}, headers=auth)
    assert voter.status_code == 201
    vote = client.post("/votes", json={"voter_id": voter.json()["id"], "candidate_id": candidate.json()["id"]})
    assert vote.status_code == 201
    duplicate = client.post("/votes", json={"voter_id": voter.json()["id"], "candidate_id": candidate.json()["id"]})
    assert duplicate.status_code == 409
    stats = client.get("/votes/statistics").json()
    assert stats["total_votes"] == 1
    assert stats["total_voters_who_voted"] == 1
    assert stats["results"][0]["percentage"] == 100.0

def test_cross_role_and_invalid_candidate(client, auth):
    assert client.post("/voters", json={"name": "Persona Uno", "email": "uno@example.com"}, headers=auth).status_code == 201
    assert client.post("/candidates", json={"name": "persona uno"}, headers=auth).status_code == 409
    voter = client.post("/voters", json={"name": "Persona Dos", "email": "dos@example.com"}, headers=auth).json()
    assert client.post("/votes", json={"voter_id": voter["id"], "candidate_id": 999}).status_code == 404

def test_protected_endpoints(client):
    assert client.get("/voters").status_code == 401

