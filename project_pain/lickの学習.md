#  lickの学習 (lick_training)

## 目標
- lickportから水報酬を得ることを学習させる
- RewardLEDの点灯と水報酬の連合を学習させる
- RewardLEDの点灯がlickを誘発できるようになれば、次の「静止の学習（gate_training）」に進む

## 状態(state)の定義
ITI, LickWait, Reward

### ITI
- ランダム長の待機時間（3.0-6.0s）。
- RewardLEDは消灯。
- 待機時間が経過したら無条件にLickWaitへ移行する。

### LickWait
- RewardLEDが点灯。
- Lickが検出されると、直ちにRewardへ移行する。
- 3.0s待ってLickが無ければ、ITIへ移行する（TimeOut）。

### Reward
- 固定長（1.0s）
- RewardLEDは消灯
- 報酬が供給される（RewardValve ON for 50ms）。
- 終了後、期間中にlickが１回でも検出されれば、LickWaitに移行する。
- lickが検出されなければ、ITIに移行する。

## トレーニングスケジュールと終了条件
- １日最長30分
- ITIに移行することなく、LickWaitとRewardの間を50回連続で往復して報酬を得られたらトレーニング終了

## pyControl
### Name of task script
tasks/pain/lick_training.py

### hardware_definitions
hardware_definitions/painTakk_channels.py

### parameters
- ITI_min: 3.0 s
- ITI_max: 6.0 s
- LickWait_length: 3.0 s
- Reward_length: 1.0 s
- RewardSize: 50 ms
- nReward: Rewardに移行したのべ回数, GUIに表示
- nMaxConsectiveReward: ITIに移行することなくLickWaitとRewardの間を往復した最高回数, GUIに表示

### mermaid
project_pain/lick_training.mmd

