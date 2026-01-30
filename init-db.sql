-- 创建翻译知识库表
CREATE TABLE IF NOT EXISTS "翻译知识库" (
    "中文" VARCHAR PRIMARY KEY,
    "英语" VARCHAR,
    "日语" VARCHAR,
    "韩语" VARCHAR
);

-- 插入示例数据
INSERT INTO "翻译知识库" ("中文", "英语", "日语", "韩语") VALUES
('天使扣', 'Angel Clip', 'エンジェルクリップ', '엔젤클립'),
('时代天使', 'Angelalign', 'Angelalign', '에인절앨라인'),
('智能手机', 'Smartphone', 'スマートフォン', '스마트폰'),
('无线耳机', 'Wireless Earphones', 'ワイヤレスイヤホン', '무선 이어폰'),
('笔记本电脑', 'Laptop', 'ノートPC', '노트북')
ON CONFLICT ("中文") DO NOTHING;

-- 显示表结构和数据
\d "翻译知识库"
SELECT * FROM "翻译知识库";
