import re

def to_zenkaku(text):
    """半角数字や記号を全角に変換する（U12/15、エリートクラス用）"""
    zenkaku_table = str.maketrans('0123456789/:~-', '０１２３４５６７８９／：〜〜')
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
        self.parse_and_categorize()

    def parse_and_categorize(self):
        # カテゴリや日付をフックにして、繋がったテキストを1イベントごとに分割
        # 例: "クラブチーム3/1（日）U10練習..." -> 日付「3/1（日）」を抽出
        pattern = re.compile(
            r'(クラブチーム|スクール|出張|MTG|会議|未定|無|確定)?'
            r'(\d{1,2}/\d{1,2}（[月火水木金土日祝]+）)(.*?)'
            r'(?=(?:クラブチーム|スクール|出張|MTG|会議|未定|無|確定)?\d{1,2}/\d{1,2}（|$)'
        )
        
        for match in pattern.finditer(self.raw_text):
            category_prefix = match.group(1) or ""
            date_str = match.group(2)
            raw_details = match.group(3)

            # MTG、会議、出張などはスケジュール出力から除外
            if category_prefix in ["出張", "MTG", "会議", "無"]:
                continue

            # 時間の抽出 (例: 9:00~12:00, 18:30-21:30)
            time_match = re.search(r'\d{1,2}:\d{2}[~-]\d{1,2}:\d{2}', raw_details)
            time_str = time_match.group(0) if time_match else ""

            # 時間より前の文字列を「タイトル＋場所」として扱う
            content_location = raw_details.split(time_str)[0].strip() if time_str else raw_details
            
            # タイトルと場所を大まかに分割（「練習」「合同」「GAME」「エリート」「ステップアップ」等を区切りにする）
            title = content_location
            location = ""
            split_match = re.search(r'(.*?練習|.*?合同|.*?GAME|.*?試合|エリート|ステップアップ)(.*)', content_location)
            if split_match:
                title = split_match.group(1).strip()
                location = split_match.group(2).replace('（フォースクラブ）', '').replace('（TAT）', '').replace('（キヅバス）', '').strip()

            event = {
                "date": date_str,
                "title": title,
                "location": location,
                "time": time_str,
                "raw_details": raw_details
            }

            self._distribute_event(event)

    def _distribute_event(self, event):
        text = event["raw_details"]
        
        # 複数該当する場合はそれぞれに格納する（例：U10,12合同練習）
        if "U10" in text:
            self.categorized_events["u10"].append(event)
        if any(k in text for k in ["U12", "U14", "U15"]):
            self.categorized_events["u12_15"].append(event)
        if "ステップアップ" in text:
            self.categorized_events["step_up"].append(event)
        if "エリート" in text:
            self.categorized_events["elite"].append(event)

    def generate_u12_15_output(self):
        output = ["【2026年３月 U12,15クラブチーム予定表】\n⚠️試合等のスケジュール変更があった場合、\nアナウンスしますので、ご確認よろしくお願い致します🙇\n"]
        for ev in self.categorized_events["u12_15"]:
            output.append(f"{to_zenkaku(ev['date'])}")
            output.append(f"{to_zenkaku(ev['title'])}")
            output.append(f"{to_zenkaku(ev['time'])}")
            output.append(f"{ev['location']}\n")
        return "\n".join(output)

    def generate_u10_output(self):
        output = ["【T's Factory U10 クラブチーム】\n2026年3月予定\n⚠️試合などが入った場合ノートで詳細アナウンス致します。\n"]
        for ev in self.categorized_events["u10"]:
            output.append(f"{ev['date']} {ev['title']}")
            if ev['location']: output.append(f"{ev['location']}")
            output.append(f"{ev['time'].replace('~', '-')}\n")
        return "\n".join(output)

    def generate_step_up_output(self):
        output = ["■ステップアップ"]
        for ev in self.categorized_events["step_up"]:
            output.append(f"{ev['date']} ステップアップ")
            if ev['location']: output.append(f"{ev['location']}")
            output.append(f"{ev['time'].replace('~', '-')}\n")
        return "\n".join(output)

    def generate_elite_output(self):
        output = ["【2026年3月エリートクラス】\nT's Factory\nエリートクラスの皆様\n日頃よりお世話になっております。\n３月のスケジュールご確認お願い致します。\n"]
        for ev in self.categorized_events["elite"]:
            output.append(f"{to_zenkaku(ev['date'])}")
            output.append(f"{to_zenkaku(ev['time'])}")
            if ev['location']: output.append(f"{ev['location']}\n")
        return "\n".join(output)

# ===== 実行用コード =====
if __name__ == "__main__":
    # ここにサンプルの入力テキストを貼り付けます
    raw_input_text = """
    クラブチーム3/1（日）U10練習中野区立明和中跡地（フォースクラブ）9:00~12:00ガク,一馬無クラブチーム3/1（日）スクール3/1（日）ステップアップ中野区立明和中跡地（フォースクラブ）18:00-21:00ガク出張3/2（月）新渡戸アフタースクール新渡戸学園16:10-17:10一馬、ノン出張3/2（月）新渡戸アフタースクール新渡戸学園17:10-18:10一馬、ノンクラブチーム3/2（月）U12,15男女練習中野区立鷺の杜小学校（TAT ）18:30-21:30知也、ガク、一馬スクール3/3（火）エリート鷺ノ杜(キヅバス)18:30-21:30知也
    """
    
    generator = ScheduleGenerator(raw_input_text)
    
    print("================ U12/15 ================")
    print(generator.generate_u12_15_output())
    
    print("================ U10 ===================")
    print(generator.generate_u10_output())
    
    print("================ ステップアップ =========")
    print(generator.generate_step_up_output())
    
    print("================ エリート ===============")
    print(generator.generate_elite_output())