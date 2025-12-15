from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__, template_folder='../templates') # 템플릿 경로 수정

# 주의: Vercel(서버리스)에서는 메모리가 초기화되므로 
# 실제 서비스라면 DB를 써야 하지만, 일단 기본 리스트를 넉넉히 넣어두는 것을 추천합니다.
registered_streamers = [
    {"id": "b5ed5db484d04faf4d150aedd362f34b", "color": "auto"}, # 강지
]

def get_chzzk_data(channel_id):
    url = f"https://api.chzzk.naver.com/service/v2/channels/{channel_id}/live-detail"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        if data['code'] == 200:
            content = data['content']
            return {
                "id": channel_id,
                "name": content['channel']['channelName'],
                "img": content['channel']['channelImageUrl'],
                "status": content['status'],
                "title": content['liveTitle'] if content['status'] == 'OPEN' else "현재 방송 중이 아닙니다.",
                "viewers": content.get('concurrentUserCount', 0),
                "category": content.get('liveCategoryValue', '정보 없음'),
            }
    except:
        return None
    return None

@app.route('/')
def index():
    display_list = []
    for s_item in registered_streamers:
        info = get_chzzk_data(s_item['id'])
        if info:
            info['bg_color'] = s_item.get('color', 'auto')
            display_list.append(info)
    return render_template('index.html', streamers=display_list)

@app.route('/add', methods=['POST'])
def add_streamer():
    channel_id = request.form.get('channel_id').strip()
    if channel_id and not any(s['id'] == channel_id for s in registered_streamers):
        registered_streamers.append({"id": channel_id, "color": "auto"})
    return redirect(url_for('index'))

@app.route('/delete/<channel_id>')
def delete_streamer(channel_id):
    global registered_streamers
    registered_streamers = [s for s in registered_streamers if s['id'] != channel_id]
    return redirect(url_for('index'))

# Vercel은 app 객체를 직접 실행하므로 이 부분은 없어도 되지만 로컬 테스트용으로 유지
if __name__ == '__main__':
    app.run(debug=True)