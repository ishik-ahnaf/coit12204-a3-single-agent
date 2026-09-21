class TestHealthEndpoint:
    def test_health(self, test_client):
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestSuggestDueDate:
    def test_valid_request(self, mocked_agent, test_client):
        response = test_client.post(
            "/api/agent/suggest_due_date",
            json={"task_title": "Write report", "task_description": "Technical report", "priority": "high"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "suggested_date" in data
        assert "state_snapshot" in data

    def test_missing_title_rejected(self, test_client):
        response = test_client.post("/api/agent/suggest_due_date", json={"task_description": "No title"})
        assert response.status_code == 422

    def test_invalid_priority_rejected(self, test_client):
        response = test_client.post(
            "/api/agent/suggest_due_date",
            json={"task_title": "Test", "priority": "urgent"},
        )
        assert response.status_code == 422


class TestClassifyPriority:
    def test_valid_request(self, mocked_agent, test_client):
        response = test_client.post(
            "/api/agent/classify_priority",
            json={"task_title": "Study for exam", "task_description": "Final exam"},
        )
        assert response.status_code == 200
        assert response.json()["priority"] in ["low", "medium", "high"]


class TestWeeklySummary:
    def test_valid_request(self, mocked_agent, test_client):
        response = test_client.post(
            "/api/agent/weekly_summary",
            json={"tasks": ["task 1", "task 2", "task 3"]},
        )
        assert response.status_code == 200
        assert response.json()["task_count"] == 3

    def test_empty_task_list_rejected(self, test_client):
        response = test_client.post("/api/agent/weekly_summary", json={"tasks": []})
        assert response.status_code == 422


class TestStateEndpoint:
    def test_get_state(self, mocked_agent, test_client):
        response = test_client.get("/api/agent/state")
        assert response.status_code == 200

    def test_reset_state(self, mocked_agent, test_client):
        response = test_client.post("/api/agent/reset")
        assert response.status_code == 200
        assert response.json()["status"] == "reset"