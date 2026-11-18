import requests
import json

headers = {"Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"}

# Test querying top clips for xqc and alanzoka
query = """
query {
  user(login: "xqc") {
    id
    login
    displayName
    clips(first: 5, criteria: { filter: ALL_TIME }) {
      edges {
        node {
          id
          slug
          title
          viewCount
          durationSeconds
          url
          videoQualities {
            sourceURL
            quality
          }
        }
      }
    }
  }
}
"""

resp = requests.post("https://gql.twitch.tv/gql", headers=headers, json={"query": query}, timeout=10)
print(json.dumps(resp.json(), indent=2))
