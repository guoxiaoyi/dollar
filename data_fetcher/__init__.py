import requests
def fetch_data(url, params=None, headers=None):
    try:
        response = requests.get("https://fapi.binance.com" + url, params=params, headers=headers)
        response.raise_for_status()  # 如果请求失败，会抛出异常
        return response.json()  # 假设返回 JSON 格式的数据
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None
    
def fetch_fng():
    try:
      response = requests.get("https://api.alternative.me/fng/?limit=5")
      response.raise_for_status()  # 如果请求失败，会抛出异常
      return response.json()  # 假设返回 JSON 格式的数据
    except requests.RequestException as e:
        print(f"获取恐慌指数失败: {e}")
        return None
