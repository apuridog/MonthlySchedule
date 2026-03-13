import streamlit as st
import re

def to_zenkaku(text):
    """半角数字や記号を全角に変換する"""
    zenkaku_table = str.maketrans('0123456789/:~-〜()', '０１２３４５６７８９／：〜〜〜（）')
    return text.translate(zenkaku_table)

class ScheduleGenerator:
    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.categorized_events = {
            "step_up": [],
            "elite": [],
            "u10": [],
            "u12_15": []
        }
        self.target_month = ""
        self.parse_and_categorize()

    def parse_and_categorize(self):
        # 改行を半角スペースに変換して、繋がったテキストとして処理
        clean_text = self.raw_text.replace('\n', ' ')

        # 日付と曜日を基準に1イベントごとに分割
        pattern = re.compile(
            r'(クラブチーム|スクール|出張|MTG|会議|未定|無|確定)?'
            r'\s*'
            r'(\d{1,2}/\d{1,2}\s*[（\(][月火水木金土日祝]+[）\)])'
            r'(.*?)'
            r'(?=(?:クラブチーム|スクール|出張|MTG|会議|未定|無|確定)?\s*\d{1,2}/\d{1,2}\s*[（\(]|$)'
        )
        
        for match in pattern.finditer(clean_text):
            category_prefix = match.group(1) or ""
            date_str = match.group(2).replace('(', '（').replace(')', '）').replace(' ', '')
            
            # テキスト内の最初の日付から「月」を自動取得
            if not self.target_month:
                month_match = re.search(r'(\d{1,2})/', date_str)
                if month_match:
                    self.target_month = month_match.group(1)

            raw_details = match.group(3).strip()

            # チームスケジュールに出力しないものを除外
            if category_prefix in ["出張", "MTG", "会議", "無"]:
                continue

            # 時間の抽出
            time_match = re.search(r'\d{1,2}:\d{2}\s*(?:[~〜～\-ー,，]+\s*\d{1,2}:\d{2})?', raw_details)
            time_str = time_match.group(0) if time_match else ""

            # 時間より前の文字列を「タイトル＋場所」として扱う
            content_location = raw_details.split(time_str)[0].strip() if time_str else raw_details
            
            # タイトルと場所の分割
            title = content_location
            location = ""
            split_match = re.search(r'(.*?練習|.*?合同|.*?GAME|.*?Game|.*?試合|エリート|ステップアップ|.*?Camp|.*?クリニック|.*?ONE)(.*)', content_location, re.IGNORECASE)
            if split_match:
                title = split_match.group(1).strip()
                location = split_match.group(2).replace('（フォースクラブ）', '').replace('（TAT）', '').replace('（TAT ）', '').replace('（キヅバス）', '').strip()

            event = {
                "date": date_str,
                "title": title,
                "location": location,
                "time": time_str.replace(' ', ''),
                "raw_details": raw_details
            }

            self._distribute_event(event)

    def _distribute_event(self, event):
        text = event["raw_details"].upper()
        title_text = event["title"].upper()

        # クラスごとに振り分け
        if "U10" in text:
            self.categorized_events["u10"].append(event)
        if any(k in text for k in ["U12", "U14", "U15"]):
            self.categorized_events["u12_15"].append(event)
        if "ステップアップ" in text or "ステップアップ" in title_text:
            self.categorized_events["step_up"].append(event)
        if "エリート" in text or "エリート" in title_text:
            self.categorized_events["elite"].append(event)

    def generate_u12_15_output(self):
        month_zenkaku = to_zenkaku(self.target_month) if self.target_month else "〇"
        output = [f"【2026年{month_zenkaku}月 U12,15クラブチーム予定表】\n⚠️試合等のスケジュール変更があった場合、\nアナウンスしますので、ご確認よろしくお願い致します🙇\n"]
        for ev in self.categorized_events["u12_15"]:
            output.append(f"{to_zenkaku(ev['date'])}")
            output.append(f"{to_zenkaku(ev['title'])}")
            if ev['time']: output.append(f"{to_zenkaku(ev['time'])}")
            if ev['location']: output.append(f"{ev['location']}")
            output.append("")
        return "\n".join(output)

    def generate_u10_output(self):
        month = self.target_month if self.target_month else "〇"
        output = [f"【T's Factory U10 クラブチーム】\n2026年{month}月予定\n⚠️試合などが入った場合ノートで詳細アナウンス致します。\n"]
        for ev in self.categorized_events["u10"]:
            output.append(f"{ev['date']} {ev['title']}")
            if ev['location']: output.append(f"{ev['location']}")
            if ev['time']: output.append(f"{ev['time'].replace('~', '-').replace('〜', '-')}")
            output.append("")
        return "\n".join(output)

    def generate_step_up_output(self):
        month = self.target_month if self.target_month else "〇"
        output = [f"【2026年{month}月スケジュール】\n\n■ステップアップ"]
        for ev in self.categorized_events["step_up"]:
            output.append(f"{ev['date']} ステップアップ")
            if ev['location']: output.append(f"{ev['location']}")
            if ev['time']: output.append(f"{ev['time'].replace('~', '-').replace('〜', '-')}")
            output.append("")
        return "\n".join(output)

    def generate_elite_output(self):
        month_zenkaku = to_zenkaku(self.target_month) if self.target_month else "〇"
        output = [f"【2026年{month_zenkaku}月エリートクラス】\nT's Factory\nエリートクラスの皆様\n日頃よりお世話になっております。\n{month_zenkaku}月のスケジュールご確認お願い致します。\n"]
        for ev in self.categorized_events["elite"]:
            output.append(f"{to_zenkaku(ev['date'])}")
            if ev['time']: output.append(f"{to_zenkaku(ev['time'])}")
            if ev['location']: output.append(f"{ev['location']}")
            output.append("")
        return "\n".join(output)


# ===== Streamlit UI（画面表示部分） =====
st.set_page_config(page_title="スケジュール自動振り分けツール", layout="centered")

st.title("🏀 月間スケジュール自動振り分けツール")
st.markdown("大元のスケジュールテキストを貼り付けると、各クラスのフォーマットに自動で振り分けます。月や改行も自動で認識します！")

# 入力エリア
raw_input_text = st.text_area("ここにテキストを貼り付けてください：", height=200)

# 実行ボタン
if st.button("スケジュールを生成する"):
    if raw_input_text.strip() == "":
        st.warning("テキストが入力されていません。")
    else:
        # 生成処理を実行
        generator = ScheduleGenerator(raw_input_text)
        
        # 取得した月があれば表示、なければ省略
        month_display = f"{generator.target_month}月の" if generator.target_month else ""
        st.success(f"{month_display}スケジュール振り分けが完了しました！以下のテキストをコピーして使用してください。")
        
        tab1, tab2, tab3, tab4 = st.tabs(["U12/15", "U10", "ステップアップ", "エリート"])
        
        with tab1:
            st.text_area("U12/15 出力結果", generator.generate_u12_15_output(), height=300)
            
        with tab2:
            st.text_area("U10 出力結果", generator.generate_u10_output(), height=300)
            
        with tab3:
            st.text_area("ステップアップ 出力結果", generator.generate_step_up_output(), height=300)
            
        with tab4:
            st.text_area("エリート 出力結果", generator.generate_elite_output(), height=300)
