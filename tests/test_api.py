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


def test_lists_details_pagination_and_deletion(client, auth):
    candidate_1 = client.post(
        "/candidates",
        json={"name": "Candidato Uno", "party": "Partido Uno"},
        headers=auth,
    ).json()

    candidate_2 = client.post(
        "/candidates",
        json={"name": "Candidato Dos", "party": "Partido Dos"},
        headers=auth,
    ).json()

    voter_1 = client.post(
        "/voters",
        json={"name": "Votante Uno", "email": "votante1@example.com"},
        headers=auth,
    ).json()

    voter_2 = client.post(
        "/voters",
        json={"name": "Votante Dos", "email": "votante2@example.com"},
        headers=auth,
    ).json()

    candidate_detail = client.get(
        f"/candidates/{candidate_1['id']}"
    )
    assert candidate_detail.status_code == 200
    assert candidate_detail.json()["name"] == "Candidato Uno"

    voter_detail = client.get(
        f"/voters/{voter_1['id']}",
        headers=auth,
    )
    assert voter_detail.status_code == 200
    assert voter_detail.json()["email"] == "votante1@example.com"

    candidates_page = client.get(
        "/candidates",
        params={"skip": 1, "limit": 1},
    )
    assert candidates_page.status_code == 200
    assert len(candidates_page.json()) == 1
    assert candidates_page.json()[0]["id"] == candidate_2["id"]

    voters_page = client.get(
        "/voters",
        params={"skip": 1, "limit": 1},
        headers=auth,
    )
    assert voters_page.status_code == 200
    assert len(voters_page.json()) == 1
    assert voters_page.json()[0]["id"] == voter_2["id"]

    assert client.delete(
        f"/voters/{voter_1['id']}",
        headers=auth,
    ).status_code == 204

    assert client.get(
        f"/voters/{voter_1['id']}",
        headers=auth,
    ).status_code == 404

    assert client.delete(
        f"/candidates/{candidate_1['id']}",
        headers=auth,
    ).status_code == 204

    assert client.get(
        f"/candidates/{candidate_1['id']}"
    ).status_code == 404


def test_vote_listing_and_protected_deletions(client, auth):
    candidate = client.post(
        "/candidates",
        json={"name": "Candidato Protegido"},
        headers=auth,
    ).json()

    voter = client.post(
        "/voters",
        json={
            "name": "Votante Protegido",
            "email": "protegido@example.com",
        },
        headers=auth,
    ).json()

    response = client.post(
        "/votes",
        json={
            "voter_id": voter["id"],
            "candidate_id": candidate["id"],
        },
    )
    assert response.status_code == 201

    votes = client.get("/votes", headers=auth)
    assert votes.status_code == 200
    assert len(votes.json()) == 1

    assert client.delete(
        f"/voters/{voter['id']}",
        headers=auth,
    ).status_code == 409

    assert client.delete(
        f"/candidates/{candidate['id']}",
        headers=auth,
    ).status_code == 409
