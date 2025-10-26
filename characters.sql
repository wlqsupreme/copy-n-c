/*
 Navicat Premium Dump SQL

 Source Server         : n-c
 Source Server Type    : PostgreSQL
 Source Server Version : 170006 (170006)
 Source Host           : aws-1-ap-south-1.pooler.supabase.com:5432
 Source Catalog        : postgres
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 170006 (170006)
 File Encoding         : 65001

 Date: 26/10/2025 11:35:15
*/


-- ----------------------------
-- Table structure for characters
-- ----------------------------
DROP TABLE IF EXISTS "public"."characters";
CREATE TABLE "public"."characters" (
  "character_id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "project_id" uuid NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "reference_image_urls" json,
  "lora_model_path" varchar(1024) COLLATE "pg_catalog"."default",
  "trigger_word" varchar(100) COLLATE "pg_catalog"."default"
)
;
COMMENT ON COLUMN "public"."characters"."character_id" IS '唯一角色ID (UUID)';
COMMENT ON COLUMN "public"."characters"."project_id" IS '外键，关联到 projects(project_id)';
COMMENT ON COLUMN "public"."characters"."name" IS '角色名称 (例如 "张三")';
COMMENT ON COLUMN "public"."characters"."description" IS '【角色外貌、性格描述】的详细描述 (例如：年龄, 性别, 身高, 体型, 发型, 发色, 眼睛, 穿着, 特殊配饰)(供大语言模型使用)';
COMMENT ON COLUMN "public"."characters"."reference_image_urls" IS '角色参考图URL列表 (JSON数组格式, 存储S3/OSS的对象存储URL)';
COMMENT ON COLUMN "public"."characters"."lora_model_path" IS '指向 S3/OSS 上的LoRA模型或Embedding文件路径 (例如 /models/lora/xxx.safetensors)';
COMMENT ON COLUMN "public"."characters"."trigger_word" IS '触发该LoRA的关键词 (例如 "ohwx_zhangsan")';
COMMENT ON TABLE "public"."characters" IS '项目角色表';

-- ----------------------------
-- Records of characters
-- ----------------------------
INSERT INTO "public"."characters" VALUES ('c0a1b2c3-1111-4f5e-8d9c-0a2a3a4a5b01', 'f47ac10b-58cc-4372-a567-0e02b2c3d479', '李慕白', '年龄17岁, 男性, 身高178cm, 身材修长, 黑色长发束成马尾, 黑色眼眸犀利, 穿着朴素的蓝色武道袍, 背着一个竹制背包和一把剑', '["https://cdn.example.com/ref/limubai_ref1.png"]', '/models/lora/project_a_limubai.safetensors', 'ohwx_limubai');
INSERT INTO "public"."characters" VALUES ('c0a1b2c3-2222-4f5e-8d9c-0a2a3a4a5b02', 'f47ac10b-58cc-4372-a567-0e02b2c3d480', '王珂', '年龄22岁, 女性, 身高165cm, 中等身材, 凌乱的黑色短发, 惊恐的大眼睛, 穿着宽大的T恤和短裤, 没有配饰', '["https://cdn.example.com/ref/wangke_ref1.png"]', '/models/lora/project_b_wangke.safetensors', 'ohwx_wangke');
INSERT INTO "public"."characters" VALUES ('508b462f-dff8-4499-8d94-2b00dea1dc76', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', '闵峙', '约35岁，男性，超A性别者（Enigma），身高约180 cm，体格健壮，常穿深色西装，眉宇间带有决断的气质，拥有异常强大的信息素能力。', '[]', NULL, NULL);
INSERT INTO "public"."characters" VALUES ('659d5eb7-0a66-4eb8-90e7-35f5d8ad8ac5', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', '付柏启', '约32岁，男性，S级Alpha，身高约185 cm，身形修长，容貌冷峻且极具魅力，常穿剪裁合体的商务西装，头发微湿，气质如高傲的天鹅。', '[]', NULL, NULL);
INSERT INTO "public"."characters" VALUES ('477adca0-ef75-4ad6-9a03-15250c0949c4', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', '方逢至', '约30岁，男性Omega，身高约178 cm，体型偏瘦略显柔弱，常穿休闲衬衫搭配牛仔裤或略显皱巴巴的商务休闲装，眉眼间带有不安与焦虑的神色，因信息素匹配度极高而常处于情绪波动的边缘。', '[]', NULL, NULL);

-- ----------------------------
-- Table structure for projects
-- ----------------------------
DROP TABLE IF EXISTS "public"."projects";
CREATE TABLE "public"."projects" (
  "project_id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "user_id" uuid NOT NULL,
  "title" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "visibility" "public"."project_visibility" DEFAULT 'private'::project_visibility,
  "default_style_prompt" text COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) DEFAULT timezone('utc'::text, now()),
  "updated_at" timestamptz(6) DEFAULT timezone('utc'::text, now()),
  "upload_method" varchar(50) COLLATE "pg_catalog"."default" DEFAULT 'single_chapter'::character varying
)
;
COMMENT ON COLUMN "public"."projects"."project_id" IS '唯一项目ID (UUID)';
COMMENT ON COLUMN "public"."projects"."user_id" IS '外键，关联到 users(user_id)，表示该项目的所有者';
COMMENT ON COLUMN "public"."projects"."title" IS '项目标题 (例如 "我的XX小说改编")';
COMMENT ON COLUMN "public"."projects"."description" IS '项目描述';
COMMENT ON COLUMN "public"."projects"."visibility" IS '可见性：private(仅自己), public(他人可见)';
COMMENT ON COLUMN "public"."projects"."default_style_prompt" IS '项目的默认风格提示词 (例如 "shonen manga, high contrast")';
COMMENT ON COLUMN "public"."projects"."created_at" IS '项目创建时间';
COMMENT ON COLUMN "public"."projects"."updated_at" IS '项目最后更新时间';
COMMENT ON TABLE "public"."projects" IS '漫画项目表';

-- ----------------------------
-- Records of projects
-- ----------------------------
INSERT INTO "public"."projects" VALUES ('f47ac10b-58cc-4372-a567-0e02b2c3d479', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '仙尘', '一部关于凡人修仙的小说改编项目', 'private', 'manga, black-and-white screentone, clean lineart, chinese ink style', '2025-10-23 17:55:37.636342+00', '2025-10-23 17:55:37.636342+00', 'single_chapter');
INSERT INTO "public"."projects" VALUES ('f47ac10b-58cc-4372-a567-0e02b2c3d480', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', '都市夜归人', '现代都市背景下的奇幻故事', 'public', 'webtoon, full color, high clarity, dynamic actionpose', '2025-10-23 17:55:37.636342+00', '2025-10-23 17:55:37.636342+00', 'single_chapter');
INSERT INTO "public"."projects" VALUES ('b7c63fe9-7c25-4122-bf59-0e9fcf34d4a6', '19602e5a-7e68-4e91-8b67-ee27d2f29bd5', '测试项目', '这是一个测试项目', 'private', NULL, '2025-10-24 01:37:31.277426+00', '2025-10-24 01:37:31.277426+00', 'single_chapter');
INSERT INTO "public"."projects" VALUES ('e7e95647-4f6f-40ef-b78f-eba6760a3ed3', '20bf06fe-5cbd-4c14-94ea-6f54ca95bb70', '测试项目', '这是一个测试项目', 'private', NULL, '2025-10-24 07:28:11.744683+00', '2025-10-24 07:28:11.744683+00', 'single_chapter');
INSERT INTO "public"."projects" VALUES ('c2349b00-6f52-4153-8e30-bf6e673066b3', '3f8f4023-9d72-4b69-a481-e5db08d91a58', '测试项目', '这是一个测试项目', 'private', NULL, '2025-10-25 07:04:10.974517+00', '2025-10-25 07:04:10.974517+00', 'single_chapter');
INSERT INTO "public"."projects" VALUES ('07235a52-140e-4ea2-b9ad-b7fb173a59a1', 'e8195641-df6b-477a-af43-d7be5981436f', '干涸地', '', 'public', '', '2025-10-25 15:55:59.152459+00', '2025-10-25 15:55:59.152459+00', 'single_chapter');
INSERT INTO "public"."projects" VALUES ('8889242a-bd61-411e-9ed6-934002ec4c4d', 'e8195641-df6b-477a-af43-d7be5981436f', '123', '', 'private', '', '2025-10-25 16:19:47.086359+00', '2025-10-25 16:19:47.086359+00', 'single_chapter');

-- ----------------------------
-- Table structure for source_texts
-- ----------------------------
DROP TABLE IF EXISTS "public"."source_texts";
CREATE TABLE "public"."source_texts" (
  "text_id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "project_id" uuid NOT NULL,
  "title" varchar(255) COLLATE "pg_catalog"."default" DEFAULT 'Untitled Chapter'::character varying,
  "raw_content" text COLLATE "pg_catalog"."default" NOT NULL,
  "order_index" int4 DEFAULT 0,
  "created_at" timestamptz(6) DEFAULT timezone('utc'::text, now()),
  "processing_status" varchar(32) COLLATE "pg_catalog"."default" DEFAULT 'pending'::character varying,
  "error_message" text COLLATE "pg_catalog"."default",
  "chapter_number" int4,
  "chapter_name" varchar(255) COLLATE "pg_catalog"."default"
)
;
COMMENT ON COLUMN "public"."source_texts"."text_id" IS '唯一文本ID (UUID)';
COMMENT ON COLUMN "public"."source_texts"."project_id" IS '外键，关联到 projects(project_id)';
COMMENT ON COLUMN "public"."source_texts"."title" IS '标题 (例如 "第一章" 或 "番外篇")';
COMMENT ON COLUMN "public"."source_texts"."raw_content" IS '存储用户上传的原始小说文本 (PostgreSQL的TEXT类型已足够)';
COMMENT ON COLUMN "public"."source_texts"."order_index" IS '用于章节或文本片段的排序';
COMMENT ON COLUMN "public"."source_texts"."created_at" IS '上传时间';
COMMENT ON COLUMN "public"."source_texts"."processing_status" IS 'AI处理状态 (pending, processing, completed, failed)';
COMMENT ON COLUMN "public"."source_texts"."error_message" IS '处理失败时的错误信息';
COMMENT ON COLUMN "public"."source_texts"."chapter_number" IS '章节编号（例如：1, 2, 3...）';
COMMENT ON COLUMN "public"."source_texts"."chapter_name" IS '章节名称（例如："第一章：下山"）';
COMMENT ON TABLE "public"."source_texts" IS '小说原文表';

-- ----------------------------
-- Records of source_texts
-- ----------------------------
INSERT INTO "public"."source_texts" VALUES ('d1b6e6e8-0b6f-4a81-8b43-6a107b7b1e2c', 'f47ac10b-58cc-4372-a567-0e02b2c3d479', '第一章：下山', '清晨，雾气尚未散去，少年李慕白背着行囊，最后看了一眼山顶的茅屋，毅然转身下山。他不知道，此行将改变他的一生。', 0, '2025-10-23 17:55:37.857842+00', 'pending', NULL, 0, '第一章：下山');
INSERT INTO "public"."source_texts" VALUES ('d1b6e6e8-0b6f-4a81-8b43-6a107b7b1e2d', 'f47ac10b-58cc-4372-a567-0e02b2c3d480', '序章：雨夜', '冰冷的雨水拍打在陈旧的窗户上。王珂缩在角落，借着闪电的光芒，她看到那个黑影又一次出现在了巷口。', 0, '2025-10-23 17:55:37.857842+00', 'pending', NULL, 0, '序章：雨夜');
INSERT INTO "public"."source_texts" VALUES ('2235f7ae-93df-42fa-9450-0a08d4b97172', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', 'Untitled Chapter', '闵峙把手中厚厚的文件扔到一旁，捏着鼻梁站了起来。

昨天暴雨下了一夜，到现在都还没停，雨点子直直地落到下去，窗上像是泼了水一样淅淅沥沥地淌着。

透过模糊的玻璃，他看到公司门口的花坛边上站着个打着灰蓝色雨伞的男人。

站了应该好一会了，裤脚都湿了大半，像是在等人。

“叩叩.....”

他收回视线，“进来。”

一个身形修长的男人从外面走进办公室，“闵总，您找我？”

见是付柏启，闵峙心绪都放松了。

凭借着自己的能力，过滤了空气中的其他味道，嗅到了男人身上令他着迷的信息素。

要说是甘菊味，但又不准确，更像是用甘菊的沐浴露洗了澡后，凑到衣服里去嗅那股味道，热烘烘的清淡味，只不过不知道为什么，最近一段时间这味道淡得不像话，快要闻不出了。

他伸手拿过付柏启今天早上交上来的文件，“你的方案有几个地方写的不太清楚，拿回去再改改。”

“是哪些地方出了问题？”

距离近了之后，甘菊味的信息素更加浓郁了，除此之外，还掺杂着一种奇怪的充满攻击性的木质香，两种味道混杂在一起就有些变味。

这并不奇怪，付柏启是一个优质的Alpha，这样的信息素才算正常。

一般来说，Alpha的信息素不像Omega那么温和，大多都沉重具有攻击性。

但闵峙很喜欢付柏启信息素的味道，不，应该说，是迷恋。

几乎每一次不经意间嗅到这股味道时他都会浑身都放松下来，就连一个人待在家里的时候也总是想着。

当然了，他也很喜欢付柏启，一个能力强，长相帅气也很识眼色的Alpha，一直都是他的理想伴侣。

是的，Alpha伴侣。

但闵峙却不是Omega，他是这个时代的超A性别者，他的两位父亲都是Alpha，因此他生来就和普通Alpha不太一样，有着比S级Alpha还要强的能力，和极具攻击性的信息素。

他并不是第一例这样的人类，研究者将他们这种群体称为Enigma。

他们凌驾于所有性别之上，他们具有侵略性的信息素甚至能将Alpha变成Omega，除了信息素之外，无论是智商还是体格都是比常人要优秀得多。

几乎整个世界的上等阶级都有他们的身影。

对于所有Enigma来说，Alpha伴侣是最好的选择，这倒是长久以来的传统了，Omega对于他们来说太过于弱小，容易伤害到他们，当然也有其他一部分原因，比如Alpha确实比Omega更能激起Enigma的欲望。

所以大部分Enigma在选择伴侣时会优先选择体格较为强健的Alpha。

不过仍有相当一部分Enigma会选择Omega，闵峙显然不是其中一员，他对Omega完全不感兴趣。

而付柏启，S级的Alpha，却长了一张冷清又漂亮的脸，个性和他的脸一样，冷淡疏离，像高傲的天鹅，总是昂着头看人。', 0, '2025-10-25 15:58:31.956235+00', 'completed', NULL, 1, '第1章 甘菊（第1页）');
INSERT INTO "public"."source_texts" VALUES ('4c67fbc2-1f92-4e03-b88f-b8e04f9673ef', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', '第1章 甘菊（第2页）', '但他有这个资本，书香世家，从小接受良好的教育，聪明又有能力。

几乎没有人会不喜欢这个漂亮的人。

闵峙也不例外。

不过很可惜的是，付柏启的性取向是omega，从他刚进公司不久大家就都知道的了。

并且他似乎也已经有一位Omega伴侣了，昨天他才看到那位娇小可人的Omega到公司门前接他。

闵峙放下笔，“你做的不错，把这些地方改了就差不多了。”

付柏启点点头，“好的，闵总。”

说完拿起文件就头也不回地出去了。

盯着被关上的门看了会儿，又把视线移到窗外。

雨小了很多，他起身望向窗外，那个打着灰蓝雨伞的男人还站在楼下，闵峙从鼻腔里沉沉地呼出气。

第二天雨就停了，窗外的阳光照得人眼睛发痛。

正要把卷帘放下，又看见站在花坛边上的男人。

他今天没有打伞，就这么在这太阳下直直地站着，从闵峙的位置看过去，只能看到一个小小的黑点。

究竟是在等谁，居然能这么刮风下雨都动也不动地等。

闵峙关上了帘子。

下午出去吃饭，刚出电梯就见有人朝着公司外窃窃私语。

闵峙朝着那边看过去，见付柏启正面露愠色地和一个男人说话，那个男人看上去有些急迫，嘴边开合地不知道在说些什么，脸上都急得发红。

“他们这是在做什么？”

正在八卦的员工见身后的闵峙吓了一跳，“闵、闵总......”

闵峙点点头，眼神望着外面的俩人，问，“那个人是谁？”

员工也困惑地摇摇头，表示不知道。

“那个男人昨天就一直站在这儿了，看来是专门等着付柏启。”

原来是站在花坛边上的那个男人。

或许是付柏启的追求者，看上去这么瘦弱，大概是个Omega或者Beta，长得也一般，就是普通的漂亮，比起上次跟在付柏启身边的Omega差了不少，更别说和付柏启相比了。

闵峙看了眼手表，正准备离开，就听不知道是谁的人在旁边说了句，“我听说，那好像是柏启的老婆......”

“什么？！”

在场的几人，包括闵峙在内都愣住了。', 1, '2025-10-25 17:40:40.382858+00', 'completed', NULL, 1, '第1章 甘菊（第2页）');
INSERT INTO "public"."source_texts" VALUES ('cf115bec-f22b-4a33-8104-5d55f04c1155', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', '第2章 夫妻（第2页）', '
男人拿着筷子的手顿了下，听见付柏启开口，“不用给我夹菜。”

“好、好的。”

看着Omega一言不发地低着头，付柏启心里也知道自己这种行为很伤人，但他没有放在心上。

这个男人叫方逢至，据说和自己的信息素匹配高达百分之百，是极为罕见的命定之番，但付柏启从来就不相信“命”

这种东西，更无法理解自己的父母竟要求自己和这个甚至都无法产生共同话题的Omega结婚。

他结婚只想要选择合适的人，像这样为了信息素在一起，比一夜情之后奉子成婚还要让人憋屈。

心里愈加烦躁，他又想起今天早上的事情来，突然放下筷子，“我说过多少次了，让你不要去我的公司，你怎么偏不听？”

其实昨天下雨的时候他就发现Omega等在公司门口，好不容易逃过去，没想到今天又来了，看着就让人心烦。

方逢至咬了咬嘴里的肉，“但是、柏启，你已经快一周没回过家了，也联系不上......我很担心你。”

“我又不是小孩子，用得着你来担心？”

最近付柏启高中时期谈的Omega男友联系上了他，他正愁着怎么释放自己被方逢至激出来的信息素，就一直跟待在一块儿，比在家里舒服多了。

他吃了几口，不想再对着方逢至这张让人烦躁的脸，头也不回地又进了书房，“没什么事情别来打扰我。”

留下方逢至独自一个人在桌前坐了好一会儿。

大概十一点左右，付柏启坐在办公桌前眼睛涩得厉害，正想休息会儿就听见房门被敲了敲。

才把门开了一个缝，就闻到了一股浓郁的甘菊味，他心里一跳，握紧门把要把门合上，但门外的Omega已经一个侧身闪了进来。

付柏启喘着气，看着面前双颊红的不像话的Omega开口：“出去。”

但Omega却没有动，而是踌躇着开口，“柏、柏启，今天妈妈打电话了......”

他低着头，手紧张地抓着裤子，“她问我们什么时候能要个孩子......”

付柏启紧紧地咬着牙，控制着自己的身体不扑到Omega身上，不得不说高匹配值的信息素确实能让人发狂，尤其是发情期的Omega，仅仅是轻轻地嗅了下，付柏启的阴茎就挺硬了，他咬牙切齿地开口：“这就是你不打抑制剂的理由？”

方逢至一愣，“不，不是的......”

身体还打着颤急忙解释：“医生说再使用抑制剂的话可能会造成信息素紊乱，可能会不定期发情......”

他难耐地夹紧双腿，伸手抓住付柏启的衣角，“柏启、标记我吧，求你了......我实在受不了了......”

付柏启握紧拳头，因为命定之番的影响，此刻他觉得方逢至比任何一个时候都要诱人，付柏启觉得心脏跳得很快，他屏着呼吸，也不敢再看Omega的脸，一把抓起方逢至的衣领把他扔到门外，也不管还在发情的Omega，紧紧地把门砸上。

他不能和这个Omega发生任何关系。

方逢至勉强支撑着靠在门上，他难受得浑身颤抖，发情期缺乏伴侣的信息素简直让人痛苦的难以忍受，他拍打着门，祈求着，“柏启、求你了......”

“柏启，我真的好难受，求你了，我会吃避孕药的，求你让我进去......”

可惜他的伴侣从来都不是个心软的人，他喊得嗓子都哑了门内也没有一点动静，就连一丁点信息素也不愿意给他。

他只好扶着墙走到浴室，打开冰凉的水浇在这具滚烫的身体上。

可即使是这样也无法缓解发情期带来的欲望，他把手抚上阴茎，又伸出手指插入后穴，咬紧了牙抽插着。

他的丈夫从来没有碰过他。

他们的第一次，仅仅才脱了衣服，他的丈夫就离开了，他说他的身体太过于干瘪瘦弱，让人没有欲望。

后来他发情期来临，差点也诱导了付柏启一起发情，但付柏启依旧不肯碰他，强制他打了抑制剂。

从那之后，他在付柏启面前就要一直贴着抑制贴，发情期要靠抑制剂度过。

他曾经幻想着丈夫会是一个温柔的男人，他会给自己足够的安全感，让他安心地度过发情期，不需要胆战心惊地使用会产生负面影响的抑制剂。

但现在完全不可能。

他的丈夫不喜欢他。

他的身体猛地一抖，高潮了。

可身体的温度却依旧降不下来，腺体的位置烫得像被放在油锅里反复煎炒，他勉强走到卧室，看着空无一人的大床，最终还是拿出了抑制剂针筒，熟练地插进手臂上的血管，把液体注射进去。', 2, '2025-10-25 18:12:29.853306+00', 'completed', NULL, 2, '第2章 夫妻（第2页）');

-- ----------------------------
-- Table structure for storyboards
-- ----------------------------
DROP TABLE IF EXISTS "public"."storyboards";
CREATE TABLE "public"."storyboards" (
  "storyboard_id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "project_id" uuid NOT NULL,
  "source_text_id" uuid NOT NULL,
  "panel_index" int4 NOT NULL DEFAULT 0,
  "original_text_snippet" text COLLATE "pg_catalog"."default",
  "character_appearance" text COLLATE "pg_catalog"."default",
  "scene_and_lighting" text COLLATE "pg_catalog"."default",
  "camera_and_composition" text COLLATE "pg_catalog"."default",
  "expression_and_action" text COLLATE "pg_catalog"."default",
  "style_requirements" text COLLATE "pg_catalog"."default",
  "generated_image_url" varchar(1024) COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) DEFAULT timezone('utc'::text, now()),
  "updated_at" timestamptz(6) DEFAULT timezone('utc'::text, now()),
  "character_id" uuid,
  "dialogue" text COLLATE "pg_catalog"."default",
  "panel_elements" jsonb
)
;
COMMENT ON COLUMN "public"."storyboards"."storyboard_id" IS '唯一分镜ID (UUID)';
COMMENT ON COLUMN "public"."storyboards"."project_id" IS '外键，关联到 projects(project_id)，用于快速索引项目下的所有分镜';
COMMENT ON COLUMN "public"."storyboards"."source_text_id" IS '外键，关联到 source_texts(text_id)，标识该分镜属于哪一章小说';
COMMENT ON COLUMN "public"."storyboards"."panel_index" IS '分镜在章节内的排序索引 (例如 0, 1, 2, ...)，用于排序';
COMMENT ON COLUMN "public"."storyboards"."original_text_snippet" IS '该分镜对应的原始小说文本片段 (方便用户对照)';
COMMENT ON COLUMN "public"."storyboards"."character_appearance" IS '【角色外貌】的详细描述 (例如：年龄, 性别, 身高, 体型, 发型, 发色, 眼睛, 穿着, 特殊配饰)';
COMMENT ON COLUMN "public"."storyboards"."scene_and_lighting" IS '【场景与光照】的详细描述 (例如：地点, 时间, 天气, 光源, 氛围)';
COMMENT ON COLUMN "public"."storyboards"."camera_and_composition" IS '【镜头与构图】的详细描述 (例如：镜头景别(特写/中景/全景), 角度(正面/四分之三/低角度/高角度), 聚焦于角色, 动态姿势)';
COMMENT ON COLUMN "public"."storyboards"."expression_and_action" IS '【表情与动作】的详细描述 (例如：情绪, 面部表情, 手势, 动作)';
COMMENT ON COLUMN "public"."storyboards"."style_requirements" IS '【风格要求】的详细描述 (例如：漫画, 黑白网点, 清晰线条, 分镜构图, 高清晰度, 详细背景, 角色设计一致性)';
COMMENT ON COLUMN "public"."storyboards"."generated_image_url" IS 'AIGC生成的漫画图片存放地址 (URL或对象存储路径)';
COMMENT ON COLUMN "public"."storyboards"."created_at" IS '分镜创建时间';
COMMENT ON COLUMN "public"."storyboards"."updated_at" IS '分镜最后更新时间';
COMMENT ON COLUMN "public"."storyboards"."character_id" IS '外键，关联到 characters(character_id)，标识该分镜的主要角色 (允许为空)';
COMMENT ON COLUMN "public"."storyboards"."dialogue" IS '【对话】的详细描述';
COMMENT ON COLUMN "public"."storyboards"."panel_elements" IS '存储面板中的多个元素，例如 [{"character_id": "uuid", "dialogue": "你好"}, {"character_id": "uuid2", "dialogue": "再见"}]';
COMMENT ON TABLE "public"."storyboards" IS '分镜规划表 (存储每个单独的漫画分格)';

-- ----------------------------
-- Records of storyboards
-- ----------------------------
INSERT INTO "public"."storyboards" VALUES ('e5a8a6f0-1b3a-4f5e-8d9c-0a2a3a4a5b61', 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 'd1b6e6e8-0b6f-4a81-8b43-6a107b7b1e2c', 0, '清晨，雾气尚未散去，少年李慕白背着行囊...', '年龄17岁, 男性, 身高178cm, 身材修长, 黑色长发束成马尾, 黑色眼眸犀利, 穿着朴素的蓝色武道袍, 背着一个竹制背包和一把剑', '山路, 清晨, 浓雾, 太阳刚升起(漫射光源), 安静且雾气缭绕的氛围', '中景镜头, 从背后呈四分之三角度, 聚焦于角色回望山顶', '怀旧, 依依不舍, 扭头回望, 静止站立', '漫画风格, 黑白网点, 清晰的线条, 详细的背景(山脉和雾气)', 'https://cdn.example.com/img/project_a_t1_p0.png', '2025-10-23 17:55:38.092062+00', '2025-10-24 02:19:27.170158+00', 'c0a1b2c3-1111-4f5e-8d9c-0a2a3a4a5b01', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('e5a8a6f0-1b3a-4f5e-8d9c-0a2a3a4a5b62', 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 'd1b6e6e8-0b6f-4a81-8b43-6a107b7b1e2c', 1, '...毅然转身下山。他不知道，此行将改变他的一生。', '年龄17岁, 男性, 身高178cm, 身材修长, 黑色长发束成马尾, 黑色眼眸犀利, 穿着朴素的蓝色武道袍, 背着一个竹制背包和一把剑', '山路, 清晨, 浓雾, 太阳刚升起(漫射光源), 安静且雾气缭绕的氛围', '全景镜头, 正面角度, 聚焦于角色向前走(朝向镜头), 动态姿势(行走中)', '坚定, 坚决, 表情严肃, 自信地大步向前', '漫画风格, 黑白网点, 清晰的线条, 强调动态的分镜构图', 'https://cdn.example.com/img/project_a_t1_p1.png', '2025-10-23 17:55:38.092062+00', '2025-10-24 02:19:27.452626+00', 'c0a1b2c3-1111-4f5e-8d9c-0a2a3a4a5b01', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('e5a8a6f0-1b3a-4f5e-8d9c-0a2a3a4a5b63', 'f47ac10b-58cc-4372-a567-0e02b2c3d480', 'd1b6e6e8-0b6f-4a81-8b43-6a107b7b1e2d', 0, '王珂缩在角落，借着闪电的光芒，她看到那个黑影又一次出现在了巷口。', '年龄22岁, 女性, 身高165cm, 中等身材, 凌乱的黑色短发, 惊恐的大眼睛, 穿着宽大的T恤和短裤, 没有配饰', '黑暗的公寓房间内, 夜晚, 雷雨, 主要光源是窗外短暂刺眼的闪电, 高对比度, 紧张的氛围', '特写镜头, 低角度(仰视角色), 聚焦于角色的脸部', '恐惧, 惊恐万分, 睁大眼睛, 用手捂住嘴巴, 蜷缩在角落', '条漫风格, 全彩, 高清晰度, 戏剧性的光照, 专注于情绪表达', 'https://cdn.example.com/img/project_b_t1_p0.png', '2025-10-23 17:55:38.092062+00', '2025-10-24 02:19:27.720621+00', 'c0a1b2c3-2222-4f5e-8d9c-0a2a3a4a5b02', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('9cd908ec-5457-4ec1-aef2-a39fbcfe6af3', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', '2235f7ae-93df-42fa-9450-0a08d4b97172', 0, '闵峙把手中厚厚的文件扔到一旁，捏着鼻梁站了起来。昨天暴雨下了一夜，到现在都还没停，雨点子直直地落到下去，窗上像是泼了水一样淅淅沥沥地淌着。透过模糊的玻璃，他看到公司门口的花坛边上站着个打着灰蓝色雨伞的男人。', '西装领口微微皱起，袖口因雨水略显湿润，眉头紧锁，手指轻捏鼻梁，眼神透过雾蒙的玻璃凝视外面。', '雨夜的办公室，窗玻璃上布满水痕，室内灯光昏暗且带有冷白色的氛围光，雨滴的光斑在玻璃上投射出斑驳的光影。', '中景推拉镜头先捕捉闵峙抛文件的动作，随后切换到浅景深的特写，焦点从闵峙的手移至窗外的雨伞男人，构图采用对角线引导视线。', '闵峙愤怒地将文件甩到一旁，随后站起身来，捏鼻子深呼吸，眼神从愤怒转为警觉。', '写实的赛博朋克风格，色调偏冷，雨水质感细腻，光影对比强烈，营造压抑而紧张的氛围。', NULL, '2025-10-25 15:58:54.802504+00', '2025-10-25 15:58:54.802504+00', '508b462f-dff8-4499-8d94-2b00dea1dc76', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('5d5cdf8e-a38e-415d-babe-c57d563804fa', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', '2235f7ae-93df-42fa-9450-0a08d4b97172', 1, '一个身形修长的男人从外面走进办公室，“闵总，您找我？”', '身形修长，灰蓝色雨伞已收起，西装剪裁合体，头发微湿贴在额头，冷峻的眼神直视闵峙，嘴角轻抿。', '办公室门口，雨水顺着门框滴落，屋内柔和的顶灯与窗外的雨光形成对比，地面有轻微的水光反射。', '跟随式推镜头从门口进入，随后切换为低角度的半身镜头捕捉付柏启的全身，构图采用三分法将人物置于画面左侧，背景的雨幕形成层次。', '付柏启步伐稳健，轻轻收起雨伞，抬头以平静却带有轻微挑衅的语气问候。', '高对比度的商业写实风，色调以冷灰蓝为主，雨滴细节清晰，人物轮廓锐利，突出角色的冷峻气质。', NULL, '2025-10-25 15:58:55.110384+00', '2025-10-25 15:58:55.110384+00', '659d5eb7-0a66-4eb8-90e7-35f5d8ad8ac5', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('36fa8209-60d0-499f-acb6-b1c50625aec9', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', '2235f7ae-93df-42fa-9450-0a08d4b97172', 2, '凭借着自己的能力，过滤了空气中的其他味道，嗅到了男人身上令他着迷的信息素。要说是甘菊味，但又不准确，更像是用甘菊的沐浴露洗了澡后，凑到衣服里去嗅那股味道，热烘烘的清淡味，只不过不知道为什么，最近一段时间这味道淡得不像话，快要闻不出了。', '闭眼轻吸，眉头舒展，面部表情放松，手指轻抚文件边缘，嘴角微微上扬，显露出沉醉的神情。', '办公室内部灯光柔和，背光形成淡淡的光晕，雨声作为背景音效，空气中似有轻微的雾气渲染出嗅觉的抽象感。', '极近景特写闵峙的鼻尖和眼睛，镜头缓慢推入，背景虚化，仅保留雨滴的光斑，构图聚焦于面部细节。', '闵峙深吸一口气，眼中闪过回忆的光芒，轻轻点头表示满意。', '感官化的艺术风格，使用柔焦和光晕效果突出嗅觉的抽象表现，色调温暖与冷色雨景形成对比。', NULL, '2025-10-25 15:58:55.409682+00', '2025-10-25 15:58:55.409682+00', '508b462f-dff8-4499-8d94-2b00dea1dc76', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('75361a08-6713-46d8-bba9-80eb4a186dbd', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', '2235f7ae-93df-42fa-9450-0a08d4b97172', 3, '他伸手拿过付柏启今天早上交上来的文件，“你的方案有几个地方写的不太清楚，拿回去再改改。”', '手指轻触文件，西装袖口微微抖动，表情严肃但带有淡淡的笑意，眼神专注。', '办公桌前的台灯投射出温暖的光柱，雨声仍在远处回响，桌面上散落几页纸张。', '两人中景，采用斜45度的侧光，构图采用对称式，闵峙位于画面左侧，付柏启位于右侧，焦点在两人手中交接的文件上。', '闵峙递文件时轻声指点，付柏启略微点头，保持冷峻的姿态。', '写实商务风格，光影柔和，色调以中性灰为主，突出人物之间的微妙张力。', NULL, '2025-10-25 15:58:55.839561+00', '2025-10-25 15:58:55.839561+00', '508b462f-dff8-4499-8d94-2b00dea1dc76', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('655693b0-7866-4a7f-b5a0-faa67819676b', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', '2235f7ae-93df-42fa-9450-0a08d4b97172', 4, '付柏启，S级的Alpha，却长了一张冷清又漂亮的脸，个性和他的脸一样，冷淡疏离，像高傲的天鹅，总是昂着头看人。', '冷清漂亮的脸庞，眉宇如雕，眼神锐利而疏离，嘴角微抿，头略微抬起，仿佛在审视整个空间。', '办公室灯光聚焦在付柏启的面部，背后形成柔和的轮廓光，雨滴的光斑在窗帘上投射出星点般的光点。', '特写肖像，采用低角度拍摄以强化其高傲气质，构图采用中心对称，背景轻度虚化。', '付柏启保持冷淡的表情，眼神略带挑衅，轻轻抬头凝视前方。', '高对比的电影质感，色调偏冷蓝，光影锐利，突出角色的高贵与疏离感。', NULL, '2025-10-25 15:58:56.091535+00', '2025-10-25 15:58:56.091535+00', '659d5eb7-0a66-4eb8-90e7-35f5d8ad8ac5', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('656f266d-7c42-40e1-a9d2-a908e36a1500', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', '4c67fbc2-1f92-4e03-b88f-b8e04f9673ef', 0, '闵峙放下笔，“你做的不错，把这些地方改了就差不多了。”付柏启点点头，“好的，闵总。”说完拿起文件就头也不回地出去了。', '身穿深色西装，领口微敞，袖口整齐，手中握着钢笔，眉头轻挑，眼神中带着审慎的满意。', '公司会议室内，柔和的顶灯光洒在长方形木桌上，窗外透进微弱的阴天光，形成轻微的光影对比。', '中景镜头，摄像机略微低角度对准闵峙的上半身，焦点在他放下笔的瞬间，背景中的付柏启略显模糊。', '闵峙轻轻点头，嘴角带有淡淡的微笑，手指轻触笔尖后放下，随后转身继续审阅文件。', '写实风格，色调偏冷，强调人物的职业气质与细腻的面部表情。', NULL, '2025-10-25 17:41:00.696839+00', '2025-10-25 17:41:00.696839+00', '508b462f-dff8-4499-8d94-2b00dea1dc76', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('b223ac20-281c-4f55-b6cb-6d9bd6e1f98f', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', '4c67fbc2-1f92-4e03-b88f-b8e04f9673ef', 1, '盯着被关上的门看了会儿，又把视线移到窗外。雨小了很多，他起身望向窗外，那个打着灰蓝雨伞的男人还站在楼下，闵峙从鼻腔里沉沉地呼出气。', '深色西装领口微敞，领带略有松动，眉头微皱，嘴角轻抿，呼气时可见淡淡的白气。', '办公室走廊尽头的落地窗外，雨滴仍在玻璃上滑落，外面的街灯投射出冷蓝色的光，室内灯光柔和。', '特写镜头，摄像机从闵峙的肩膀后方拍摄，焦点在他的眼神与窗外的雨伞，背景略显模糊。', '闵峙站起身，抬头凝视窗外，深吸一口气后缓缓呼出，眼神中带有淡淡的思索。', '略带电影感的光影处理，雨滴细节清晰，整体色调冷峻，突出人物的孤独感。', NULL, '2025-10-25 17:41:01.097762+00', '2025-10-25 17:41:01.097762+00', '508b462f-dff8-4499-8d94-2b00dea1dc76', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('74f016e2-82bc-4623-83cc-e2cffc72a161', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', '4c67fbc2-1f92-4e03-b88f-b8e04f9673ef', 2, '第二天雨就停了，窗外的阳光照得人眼睛发痛。正要把卷帘放下，又看见站在花坛边上的男人。他今天没有打伞，就这么在这太阳下直直地站着，从闵峙的位置看过去，只能看到一个小小的黑点。', '西装领口敞开，领带微微倾斜，眉头紧锁，眼睛因强光微眯，手指轻触卷帘的拉绳。', '公司大窗前的花坛，阳光强烈，光线直射在花坛的草地上，形成鲜明的光斑与阴影。', '广角镜头，摄像机位于闵峙的视角，前景是卷帘的拉绳，背景是远处的黑点人物，光线从左侧斜射。', '闵峙抬手欲拉下卷帘，瞬间停住，目光锁定远处的黑点，眉头微皱，显露出不解与好奇。', '高对比度的光影，阳光的刺眼感要突出，人物与背景的色彩对比鲜明，营造紧张的氛围。', NULL, '2025-10-25 17:41:01.443829+00', '2025-10-25 17:41:01.443829+00', '508b462f-dff8-4499-8d94-2b00dea1dc76', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('37070fc6-9150-41d7-acae-69c3230df384', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', '4c67fbc2-1f92-4e03-b88f-b8e04f9673ef', 3, '下午出去吃饭，刚出电梯就见有人朝着公司外窃窃私语。闵峙朝着那边看过去，见付柏启正面露愠色地和一个男人说话，那个男人看上去有些急迫，嘴边开合地不知道在说些什么，脸上都急得发红。', '剪裁合体的商务西装，领口敞开露出微湿的发丝，眉头紧锁，面颊因愤怒而泛红，眼神锐利。', '公司大堂的玻璃门口，外面阳光透过玻璃洒进来，形成斑驳的光影，周围有几位员工低声交谈。', '中景镜头，摄像机略微仰视付柏启，左侧留出与他对话的男人的身影，背景中可见闵峙的侧脸。', '付柏启嘴角紧抿，眉头紧皱，手指轻敲胸前口袋，显露出不耐烦与愠怒。', '写实且略带戏剧化的色调，强调付柏启的愤怒表情与面部红晕，光线聚焦在人物面部。', NULL, '2025-10-25 17:41:01.775659+00', '2025-10-25 17:41:01.775659+00', '659d5eb7-0a66-4eb8-90e7-35f5d8ad8ac5', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('a59a4e88-1795-41b6-a4d7-1ba423aea427', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', '4c67fbc2-1f92-4e03-b88f-b8e04f9673ef', 4, '“他们这是在做什么？”正在八卦的员工见身后的闵峙吓了一跳，“闵、闵总......”闵峙点点头，眼神望着外面的俩人，问，“那个人是谁？”员工也困惑地摇摇头，表示不知道。', '深色西装领口微敞，眉头微挑，眼神锐利而带有探询，手轻抚下巴。', '公司走廊尽头的玻璃门口，外面光线明亮，内部灯光柔和，几名员工站在门口形成半圆。', '两人对话的中景，摄像机在闵峙与员工之间切换，先聚焦闵峙的侧脸，再转向员工的惊讶表情。', '闵峙轻轻点头，眉头微皱，声音低沉而带有询问的力度；员工面露惊慌，嘴巴微张。', '细腻的面部特写，光线柔和但突出人物的眼神，整体色调保持冷静的商务氛围。', NULL, '2025-10-25 17:41:02.108638+00', '2025-10-25 17:41:02.108638+00', '508b462f-dff8-4499-8d94-2b00dea1dc76', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('3cada6da-0e89-456f-a26d-898f9975aee9', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', '4c67fbc2-1f92-4e03-b88f-b8e04f9673ef', 5, '闵峙看了眼手表，正准备离开，就听不知道是谁的人在旁边说了句，“我听说，那好像是柏启的老婆......”“什么？！”在场的几人，包括闵峙在内都愣住了。', '西装领口敞开，手腕轻抚手表，眼睛睁大，嘴巴微张，表情从平静瞬间转为震惊。', '公司走廊的灯光略显昏暗，墙面投射出柔和的阴影，背景中几位员工的身影被拉长。', '特写镜头，摄像机聚焦闵峙的面部表情，随后快速拉远至全景，捕捉所有人惊讶的姿态。', '闵峙抬手指向手表，随后眉头骤然抬起，嘴巴张开发出惊呼，身体微微后仰。', '高对比度的光影，突出人物的惊讶表情，整体色调保持冷色调以衬托紧张氛围。', NULL, '2025-10-25 17:41:02.469716+00', '2025-10-25 17:41:02.469716+00', '508b462f-dff8-4499-8d94-2b00dea1dc76', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('42df7062-142e-4ebd-8c6a-c30f82ad42eb', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', 'cf115bec-f22b-4a33-8104-5d55f04c1155', 0, '男人拿着筷子的手顿了下，听见付柏启开口，“不用给我夹菜。”', '身着深色剪裁合体的商务西装，领口微敞，手指轻轻握住筷子，眉头微皱，眼神冷峻而带有轻蔑。', '餐厅内灯光柔和，侧光从窗外射入，形成淡淡的光晕，桌面上有几盏小蜡烛投射出温暖的橙色光斑。', '中景镜头，摄像机略微低角度对准付柏启的上半身，构图以他为中心，左侧留出空位暗示对面的方逢至。', '付柏启轻声说话，嘴角微抿，手指轻颤，显露出不耐烦的情绪。', '写实风格，色调偏冷，强调人物的冷峻气质与餐桌的温暖对比。', NULL, '2025-10-25 18:13:26.134134+00', '2025-10-25 18:13:26.134134+00', '659d5eb7-0a66-4eb8-90e7-35f5d8ad8ac5', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('96b40859-341e-4ff6-b2f4-06ffc57f2e35', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', 'cf115bec-f22b-4a33-8104-5d55f04c1155', 1, '方逢至咬了咬嘴里的肉，“但是、柏启，你已经快一周没回过家了，也联系不上......我很担心你。”', '穿着略显皱巴巴的浅色衬衫，领口微敞，嘴里残留肉屑，眉头紧锁，眼中带着焦虑与恳求。', '同一餐桌，灯光仍为柔和的暖光，但聚焦在方逢至的面部，形成轻微的背光轮廓。', '特写镜头，摄像机对准方逢至的侧脸，浅景深让背景略显模糊，仅保留餐具的轮廓。', '方逢至低头咬肉，随后抬头直视付柏启，声音颤抖，手指不自觉地抚摸胸口。', '细腻写实，突出角色的情感波动，使用柔和的光线渲染焦虑氛围。', NULL, '2025-10-25 18:13:26.413704+00', '2025-10-25 18:13:26.413704+00', '477adca0-ef75-4ad6-9a03-15250c0949c4', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('75754200-2c74-42ae-aea2-a3708dc2f26a', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', 'cf115bec-f22b-4a33-8104-5d55f04c1155', 2, '他吃了几口，不想再对着方逢至这张让人烦躁的脸，头也不回地又进了书房，“没什么事情别来打扰我。”', '西装外套略显紧绷，领口微微敞开，眉头紧锁，眼神冷漠，手指轻敲桌面后站起。', '餐厅灯光逐渐暗淡，走廊灯光为冷白色，投射出硬朗的光线。', '跟随镜头，从餐桌拉至门口，采用平移镜头捕捉付柏启离开的背影，构图采用对称的走廊线条。', '付柏启站起，快速步入书房，背影坚决，肩膀微微前倾。', '冷色调，强调角色的决绝与空间的冷峻感。', NULL, '2025-10-25 18:13:26.708206+00', '2025-10-25 18:13:26.708206+00', '659d5eb7-0a66-4eb8-90e7-35f5d8ad8ac5', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('5a6a416e-686f-428d-b31f-4520f97141d5', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', 'cf115bec-f22b-4a33-8104-5d55f04c1155', 3, '大概十一点左右，付柏启坐在办公桌前眼睛涩得厉害，正想休息会儿就听见房门被敲了敲。', '坐在办公桌前，西装领口微微敞开，眼睛红肿，眉头紧锁，手指轻抚额头。', '书房内灯光为柔和的台灯光，光线聚焦在桌面，周围略显暗淡，营造夜晚的孤寂感。', '中景镜头，摄像机从侧面捕捉付柏启的侧脸与敲门的声音同步出现的门把手特写。', '付柏启抬头，眼神疲惫却带有警觉，手指轻轻敲击桌面，显示出不安。', '低光写实，使用柔和的灯光与阴影对比，突出人物的疲惫感。', NULL, '2025-10-25 18:13:27.014657+00', '2025-10-25 18:13:27.014657+00', '659d5eb7-0a66-4eb8-90e7-35f5d8ad8ac5', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('70373fd1-89f1-473c-86cb-7dc8bd1dbbe5', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', 'cf115bec-f22b-4a33-8104-5d55f04c1155', 4, '才把门开了一个缝，就闻到了一股浓郁的甘菊味，他心里一跳，握紧门把要把门合上，但门外的Omega已经一个侧身闪了进来。', '侧身进入，衬衫领口敞开，双颊通红，眼中带泪光，手指轻颤，衣领微微皱起。', '门口的走廊灯光投射出淡淡的黄色光束，甘菊的香气以视觉化的淡淡光晕表现。', '低角度特写，摄像机对准方逢至的侧脸与红润的双颊，背景模糊的门框形成框架。', '方逢至眉头紧锁，嘴唇轻颤，眼神恳求，身体微微前倾。', '略带梦幻的光晕效果，突出甘菊味的视觉化表现，保持写实人物细节。', NULL, '2025-10-25 18:13:27.330077+00', '2025-10-25 18:13:27.330077+00', '477adca0-ef75-4ad6-9a03-15250c0949c4', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('6cedc2a6-f8f9-4041-b392-976c13e8bab0', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', 'cf115bec-f22b-4a33-8104-5d55f04c1155', 5, '付柏启喘着气，看着面前双颊红的不像话的Omega开口：“出去。”', '站在门口，西装外套略显皱巴，眉头紧锁，嘴角紧闭，手握门把，呼吸急促。', '门口的灯光投射出硬朗的白光，形成强烈的光影对比，背景的书房灯光仍为柔和的黄光。', '中景镜头，摄像机在门框内侧，捕捉付柏启的正面与方逢至的背影形成对比。', '付柏启声音低沉，眼神冷漠，手指紧紧抓住门把，身体微微前倾。', '高对比度，冷暖光交织，突出角色的冲突与紧张气氛。', NULL, '2025-10-25 18:13:27.619596+00', '2025-10-25 18:13:27.619596+00', '659d5eb7-0a66-4eb8-90e7-35f5d8ad8ac5', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('f2f712fd-a33a-48b1-879a-c30e9ce8a592', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', 'cf115bec-f22b-4a33-8104-5d55f04c1155', 6, '方逢至一愣，“不，不是的......”身体还打着颤急忙解释：“医生说再使用抑制剂的话可能会造成信息素紊乱，可能会不定期发情......”', '双手紧抓付柏启的衣角，衣领被抓得微微皱起，眼中泪光闪烁，嘴唇颤抖，身体微微颤抖。', '门口的灯光仍为硬白光，方逢至的面部被柔和的背光勾勒出轮廓，形成光环效果。', '特写镜头，摄像机聚焦在方逢至的手部与眼神，背景的门框形成自然框架。', '方逢至声音颤抖，眼泪几乎要掉下来，身体不住颤抖，手指紧抓衣角。', '细腻写实，使用浅景深突出情感细节，光线柔和以衬托角色的脆弱。', NULL, '2025-10-25 18:13:27.933721+00', '2025-10-25 18:13:27.933721+00', '477adca0-ef75-4ad6-9a03-15250c0949c4', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('3f5d4a3e-abfa-445f-9fb6-99a1dd09fced', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', 'cf115bec-f22b-4a33-8104-5d55f04c1155', 7, '付柏启握紧拳头，因为命定之番的影响，此刻他觉得方逢至比任何一个时候都要诱人，付柏启觉得心脏跳得很快，他屏着呼吸，也不敢再看Omega的脸，一把抓起方逢至的衣领把他扔到门外，也不管还在发情的Omega，紧紧地把门砸上。', '拳头紧握，西装外套被扯出一道裂痕，眉头紧锁，眼神狂怒且充满压抑的欲望，呼吸急促。', '门外的走廊灯光强烈，门被猛力砸上时产生的冲击光晕，室内灯光瞬间被遮挡，形成暗黑瞬间。', '快速切换的近景与动作镜头，摄像机跟随付柏启的手部动作，捕捉衣领被抓起的瞬间以及门被砸上的冲击特写。', '付柏启怒吼，身体前倾，手臂用力抓起方逢至的衣领，将其甩出门外，随后用力将门砸上，拳头仍紧握。', '动感强烈的动作镜头，使用高速快门捕捉冲击瞬间，色调偏暗，突出暴力与压抑的情绪。', NULL, '2025-10-25 18:13:28.224857+00', '2025-10-25 18:13:28.224857+00', '659d5eb7-0a66-4eb8-90e7-35f5d8ad8ac5', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('9da72554-e3d2-4a26-83fa-0df6e6fd68f6', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', 'cf115bec-f22b-4a33-8104-5d55f04c1155', 8, '方逢至勉强支撑着靠在门上，他难受得浑身颤抖，发情期缺乏伴侣的信息素简直让人痛苦的难以忍受，他拍打着门，祈求着，“柏启、求你了......”', '衣衫略显皱褶，汗珠顺着额头滑落，眼眶红肿，手指用力拍打门框。', '昏暗的走廊，门后投射出冷蓝色的光柱，门缝透出微弱的光，营造出压抑的氛围。', '低角度镜头仰视方逢至，门框占据画面左侧，人物位于画面中心偏右，焦点拉近至颤抖的手。', '面容扭曲，嘴唇颤抖，眼神充满绝望与恳求，身体微微前倾，手掌用力拍击门面。', '写实风格，强调光影对比，突出角色的痛苦与无助感。', NULL, '2025-10-25 18:13:28.534027+00', '2025-10-25 18:13:28.534027+00', '477adca0-ef75-4ad6-9a03-15250c0949c4', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('438ffe21-f60b-4c5f-8dea-a32066c59137', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', 'cf115bec-f22b-4a33-8104-5d55f04c1155', 9, '可惜他的伴侣从来都不是个心软的人，他喊得嗓子都哑了门内也没有一点动静，就连一丁点信息素也不愿意给他。', '站在门后，身着剪裁合体的深色商务西装，头发微湿，面容冷峻，眼神淡漠。', '门内的灯光冷白，形成强硬的光线，映照在付柏启的侧脸，形成锐利的阴影。', '切换到门内的中景，付柏启站在门框中央，构图对称，背景虚化以突出人物。', '眉头微皱，嘴角轻轻抿起，毫不动容地站立，手指轻轻搭在门把手上。', '冷色调，强调角色的高傲与冷漠，使用硬光营造金属感。', NULL, '2025-10-25 18:13:28.83047+00', '2025-10-25 18:13:28.83047+00', '659d5eb7-0a66-4eb8-90e7-35f5d8ad8ac5', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('69ee8698-099f-47c9-92c6-b7b329eed750', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', 'cf115bec-f22b-4a33-8104-5d55f04c1155', 10, '他只好扶着墙走到浴室，打开冰凉的水浇在这具滚烫的身体上。', '身穿半脱的白色衬衫，肩膀微颤，头发因冷水而微微湿润，眼中仍带泪光。', '浴室灯光为柔和的白色，水流产生的细碎光斑在墙面上跳动，营造出冷冽的氛围。', '侧面跟随镜头，手持摄像机从背后跟随方逢至的步伐，最后定格在他打开水龙头的瞬间。', '双手扶墙，身体微微前倾，水流倾泻在胸口，眉头紧锁，呼吸急促。', '细腻的水滴特写，使用慢速快门制造水雾效果，突出冷暖对比。', NULL, '2025-10-25 18:13:29.117084+00', '2025-10-25 18:13:29.117084+00', '477adca0-ef75-4ad6-9a03-15250c0949c4', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('61541e7f-cd16-4903-9ad4-4bab74ae4e55', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', 'cf115bec-f22b-4a33-8104-5d55f04c1155', 11, '可即使是这样也无法缓解发情期带来的欲望，他把手抚上阴茎，又伸出手指插入后穴，咬紧了牙抽插着。', '半裸状态，皮肤因冷水而微微发光，手指紧握，眉头紧绷，牙齿咬紧。', '浴室的灯光投射出柔和的阴影，水汽在空气中形成轻雾，光线在皮肤上形成光斑。', '特写镜头聚焦在手部动作与面部表情之间的切换，使用浅景深模糊背景。', '眼神空洞，嘴角微微抽搐，身体微微颤抖，手部动作急促而重复。', '写实且略带暗色调，突出角色的绝望与自我折磨。', NULL, '2025-10-25 18:13:29.448109+00', '2025-10-25 18:13:29.448109+00', '477adca0-ef75-4ad6-9a03-15250c0949c4', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('684e799c-341b-4c3e-bb28-43fe23a05264', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', 'cf115bec-f22b-4a33-8104-5d55f04c1155', 12, '他的身体猛地一抖，高潮了。可身体的温度却依旧降不下来，腺体的位置烫得像被放在油锅里反复煎炒，他勉强走到卧室，看着空无一人的大床，最终还是拿出了抑制剂针筒，熟练地插进手臂上的血管，把液体注射进去。', '全身赤裸，皮肤因高温而微红，手臂上显露出注射针筒的细节，眼神中混合着痛苦与决绝。', '卧室灯光为暗黄灯泡，营造出沉闷的氛围，床铺空荡，光线从窗帘缝隙投射进来形成斑驳光影。', '从床头的俯视角度拍摄，方逢至站在床边，针筒特写在手臂上，背景虚化突出动作。', '眉头紧锁，嘴唇微抿，手稳稳握住针筒，注射时眼神坚定，随后深呼吸。', '使用冷暖对比的色调，突出身体的炽热感与房间的冷寂感，整体风格写实且带有压抑的氛围。', NULL, '2025-10-25 18:13:29.768157+00', '2025-10-25 18:13:29.768157+00', '477adca0-ef75-4ad6-9a03-15250c0949c4', NULL, NULL);
INSERT INTO "public"."storyboards" VALUES ('b4ac8b20-f656-418f-adad-a12902672257', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', '2235f7ae-93df-42fa-9450-0a08d4b97172', 5, '他伸手拿过付柏启今天早上交上来的文件，“你的方案有几个地方写的不太清楚，拿回去再改改。” “是哪些地方出了问题？”', '闵峙坐在办公桌后，表情严肃；付柏启站在桌前，略显疑惑。', '办公室内，台灯提供主要光源，窗外是雨景', '中景，过肩镜头，先显示闵峙说话，然后切换到付柏启', '闵峙手指点文件，略带不满；付柏启微微皱眉，询问', '写实商务风格, 强调人物互动', NULL, '2025-10-26 03:28:18.044359+00', '2025-10-26 03:28:18.044359+00', '508b462f-dff8-4499-8d94-2b00dea1dc76', NULL, '[{"dialogue": "你的方案有几个地方写的不太清楚，拿回去再改改。", "character_id": "508b462f-dff8-4499-8d94-2b00dea1dc76"}, {"dialogue": "是哪些地方出了问题？", "character_id": "659d5eb7-0a66-4eb8-90e7-35f5d8ad8ac5"}]');
INSERT INTO "public"."storyboards" VALUES ('26f9d122-9932-47bf-9254-6c707d23faa9', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', 'cf115bec-f22b-4a33-8104-5d55f04c1155', 13, '男人拿着筷子的手顿了下，听见付柏启开口，“不用给我夹菜。” “好、好的。”', '付柏启表情冷淡；方逢至低头，显得顺从。', '餐厅，餐桌上菜肴丰盛，灯光柔和', '双人中景，餐桌两侧相对而坐', '付柏启放下筷子，语气冷漠；方逢至手一顿，小声回应', '生活化场景, 暖色调', NULL, '2025-10-26 03:28:18.044359+00', '2025-10-26 03:28:18.044359+00', '659d5eb7-0a66-4eb8-90e7-35f5d8ad8ac5', NULL, '[{"dialogue": "不用给我夹菜。", "character_id": "659d5eb7-0a66-4eb8-90e7-35f5d8ad8ac5"}, {"dialogue": "好、好的。", "character_id": "477adca0-ef75-4ad6-9a03-15250c0949c4"}]');
INSERT INTO "public"."storyboards" VALUES ('c9b14f8e-20a5-4af1-8c08-e8632a3f0c57', '07235a52-140e-4ea2-b9ad-b7fb173a59a1', 'cf115bec-f22b-4a33-8104-5d55f04c1155', 14, '他拍打着门，祈求着，“柏启、求你了......”“柏启，我真的好难受，求你了，我会吃避孕药的，求你让我进去......”可惜他的伴侣从来都不是个心软的人...', '方逢至靠在门上，衣衫凌乱，泪眼婆娑。', '昏暗的走廊，门缝透出冷光', '特写镜头，聚焦方逢至绝望的表情和拍门的手', '哭泣，拍门，声音嘶哑，身体颤抖', '强调悲伤和绝望感', NULL, '2025-10-26 03:28:18.044359+00', '2025-10-26 03:28:18.044359+00', '477adca0-ef75-4ad6-9a03-15250c0949c4', NULL, '[{"dialogue": "柏启、求你了......", "character_id": "477adca0-ef75-4ad6-9a03-15250c0949c4"}, {"dialogue": "柏启，我真的好难受，求你了，我会吃避孕药的，求你让我进去......", "character_id": "477adca0-ef75-4ad6-9a03-15250c0949c4"}, {"dialogue": "(旁白) 可惜他的伴侣从来都不是个心软的人...", "character_id": null}]');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS "public"."users";
CREATE TABLE "public"."users" (
  "user_id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "username" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "email" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "hashed_password" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "credit_balance" int4 DEFAULT 0,
  "created_at" timestamptz(6) DEFAULT timezone('utc'::text, now()),
  "updated_at" timestamptz(6) DEFAULT timezone('utc'::text, now())
)
;
COMMENT ON COLUMN "public"."users"."user_id" IS '唯一用户ID (UUID)';
COMMENT ON COLUMN "public"."users"."username" IS '用户名 (用于登录，必须唯一)';
COMMENT ON COLUMN "public"."users"."email" IS '电子邮箱 (用于登录或找回密码，必须唯一)';
COMMENT ON COLUMN "public"."users"."hashed_password" IS '加密后的密码 (例如使用bcrypt或Argon2)';
COMMENT ON COLUMN "public"."users"."credit_balance" IS '可使用额度 (例如: 剩余可生成图片张数或Token数)';
COMMENT ON COLUMN "public"."users"."created_at" IS '账户创建时间';
COMMENT ON COLUMN "public"."users"."updated_at" IS '账户信息最后更新时间';
COMMENT ON TABLE "public"."users" IS '用户信息表';

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO "public"."users" VALUES ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'user_A', 'user_a@example.com', '$2b$12$dummyhashplaceholder1', 100, '2025-10-23 17:55:37.406081+00', '2025-10-23 17:55:37.406081+00');
INSERT INTO "public"."users" VALUES ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'user_B', 'user_b@example.com', '$2b$12$dummyhashplaceholder2', 50, '2025-10-23 17:55:37.406081+00', '2025-10-23 17:55:37.406081+00');
INSERT INTO "public"."users" VALUES ('19602e5a-7e68-4e91-8b67-ee27d2f29bd5', 'test_user_1864', 'test_user_1864@example.com', 'test_password_hash', 0, '2025-10-24 01:37:30.692544+00', '2025-10-24 01:37:30.692544+00');
INSERT INTO "public"."users" VALUES ('5cfa3d74-920b-4f57-9ad2-f02838b56c22', 'test_user_create', 'test_create@example.com', '$2b$12$Tew/dJ9.gg7waD9Bv.XV8us1PvcDl3jbym96kBJzw.kFUqUXnFhWe', 0, '2025-10-24 01:39:16.413759+00', '2025-10-24 01:39:16.413759+00');
INSERT INTO "public"."users" VALUES ('20bf06fe-5cbd-4c14-94ea-6f54ca95bb70', 'test_user_22904', 'test_user_22904@example.com', '$2b$12$ciGPhTm/e2QpsQhAlLYxVekcM4FcYQmF13S//6qgzQGQtN/LQ7Or6', 0, '2025-10-24 07:28:10.851147+00', '2025-10-24 07:28:10.851147+00');
INSERT INTO "public"."users" VALUES ('3f8f4023-9d72-4b69-a481-e5db08d91a58', 'test_user_666341', 'test_user_666341@example.com', 'test_password_hash', 0, '2025-10-25 07:04:06.872929+00', '2025-10-25 07:04:06.872929+00');
INSERT INTO "public"."users" VALUES ('e8195641-df6b-477a-af43-d7be5981436f', '123', '123@123.com', '$2b$12$.yGbA59y5Ijn05ptFxK0ouW4i41DLR.2O1bw/t85NPdJdyT9VKFEK', 0, '2025-10-25 13:56:14.043823+00', '2025-10-25 13:56:14.043823+00');

-- ----------------------------
-- Primary Key structure for table characters
-- ----------------------------
ALTER TABLE "public"."characters" ADD CONSTRAINT "characters_pkey" PRIMARY KEY ("character_id");

-- ----------------------------
-- Triggers structure for table projects
-- ----------------------------
CREATE TRIGGER "set_projects_updated_at" BEFORE UPDATE ON "public"."projects"
FOR EACH ROW
EXECUTE PROCEDURE "public"."trigger_set_timestamp"();

-- ----------------------------
-- Primary Key structure for table projects
-- ----------------------------
ALTER TABLE "public"."projects" ADD CONSTRAINT "projects_pkey" PRIMARY KEY ("project_id");

-- ----------------------------
-- Indexes structure for table source_texts
-- ----------------------------
CREATE INDEX "idx_source_texts_chapter_number" ON "public"."source_texts" USING btree (
  "project_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "chapter_number" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table source_texts
-- ----------------------------
ALTER TABLE "public"."source_texts" ADD CONSTRAINT "source_texts_pkey" PRIMARY KEY ("text_id");

-- ----------------------------
-- Indexes structure for table storyboards
-- ----------------------------
CREATE INDEX "idx_storyboards_panel_elements" ON "public"."storyboards" USING gin (
  "panel_elements" "pg_catalog"."jsonb_ops"
);

-- ----------------------------
-- Triggers structure for table storyboards
-- ----------------------------
CREATE TRIGGER "set_storyboards_updated_at" BEFORE UPDATE ON "public"."storyboards"
FOR EACH ROW
EXECUTE PROCEDURE "public"."trigger_set_timestamp"();

-- ----------------------------
-- Primary Key structure for table storyboards
-- ----------------------------
ALTER TABLE "public"."storyboards" ADD CONSTRAINT "storyboards_pkey" PRIMARY KEY ("storyboard_id");

-- ----------------------------
-- Triggers structure for table users
-- ----------------------------
CREATE TRIGGER "set_users_updated_at" BEFORE UPDATE ON "public"."users"
FOR EACH ROW
EXECUTE PROCEDURE "public"."trigger_set_timestamp"();

-- ----------------------------
-- Uniques structure for table users
-- ----------------------------
ALTER TABLE "public"."users" ADD CONSTRAINT "users_username_key" UNIQUE ("username");
ALTER TABLE "public"."users" ADD CONSTRAINT "users_email_key" UNIQUE ("email");

-- ----------------------------
-- Primary Key structure for table users
-- ----------------------------
ALTER TABLE "public"."users" ADD CONSTRAINT "users_pkey" PRIMARY KEY ("user_id");

-- ----------------------------
-- Foreign Keys structure for table characters
-- ----------------------------
ALTER TABLE "public"."characters" ADD CONSTRAINT "characters_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "public"."projects" ("project_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table projects
-- ----------------------------
ALTER TABLE "public"."projects" ADD CONSTRAINT "projects_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users" ("user_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table source_texts
-- ----------------------------
ALTER TABLE "public"."source_texts" ADD CONSTRAINT "source_texts_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "public"."projects" ("project_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table storyboards
-- ----------------------------
ALTER TABLE "public"."storyboards" ADD CONSTRAINT "storyboards_character_id_fkey" FOREIGN KEY ("character_id") REFERENCES "public"."characters" ("character_id") ON DELETE SET NULL ON UPDATE NO ACTION;
ALTER TABLE "public"."storyboards" ADD CONSTRAINT "storyboards_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "public"."projects" ("project_id") ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE "public"."storyboards" ADD CONSTRAINT "storyboards_source_text_id_fkey" FOREIGN KEY ("source_text_id") REFERENCES "public"."source_texts" ("text_id") ON DELETE CASCADE ON UPDATE NO ACTION;
