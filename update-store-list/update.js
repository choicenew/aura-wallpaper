const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');

async function main() {
  try {
    // 1. 获取包名 (可通过环境变量 PACKAGE_NAME 或命令行参数传入)
    const packageName = process.env.PACKAGE_NAME || process.argv[2];
    if (!packageName) {
      console.error('❌ 错误: 未配置 PACKAGE_NAME 环境变量或命令行参数。');
      process.exit(1);
    }

    // 2. 获取 Google Play API 密钥凭证文件路径
    const keyFilePath = process.env.KEY_FILE
      ? path.resolve(process.env.KEY_FILE)
      : path.join(__dirname, '../play_config.json');

    if (!fs.existsSync(keyFilePath)) {
      console.error(`❌ 错误: 找不到 Play Store Service Account 凭证文件: ${keyFilePath}`);
      process.exit(1);
    }

    // 3. 确定翻译 JSON 文件路径
    let targetFileName = process.env.TRANSLATIONS_FILE || 'translations.json';
    let jsonPath = path.isAbsolute(targetFileName)
      ? targetFileName
      : path.join(__dirname, targetFileName);

    // 如果指定的翻译文件不存在，退而求其次寻找默认 translations.json
    if (!fs.existsSync(jsonPath)) {
      const fallbackPath = path.join(__dirname, 'translations.json');
      if (fs.existsSync(fallbackPath)) {
        console.log(`⚠️ 指定文件 [${targetFileName}] 不存在，降级使用默认 [translations.json]`);
        jsonPath = fallbackPath;
      } else {
        console.error(`❌ 错误: 找不到翻译 JSON 文件: ${jsonPath}`);
        process.exit(1);
      }
    }

    // 4. 读取并校验 JSON 内容
    console.log(`📖 正在读取翻译文件: ${jsonPath}`);
    const rawContent = fs.readFileSync(jsonPath, 'utf8').trim();
    if (!rawContent || rawContent === '{}') {
      console.log('ℹ️ 翻译 JSON 文件内容为空，无需更新 Store Listing。');
      return;
    }

    let translations;
    try {
      translations = JSON.parse(rawContent);
    } catch (parseError) {
      console.error(`❌ 错误: 翻译 JSON 解析失败: ${parseError.message}`);
      process.exit(1);
    }

    const languages = Object.keys(translations);
    if (languages.length === 0) {
      console.log('ℹ️ 翻译 JSON 中不包含任何语言条目，跳过更新。');
      return;
    }

    console.log(`🔍 识别到 ${languages.length} 种语言条目: ${languages.join(', ')}`);

    // 5. 初始化 Google Play API 客户端
    const auth = new google.auth.GoogleAuth({
      keyFile: keyFilePath,
      scopes: ['https://www.googleapis.com/auth/androidpublisher']
    });
    const publisher = google.androidpublisher({ version: 'v3', auth });

    // 6. 开启 Edit 事务
    console.log(`\n1. 开启 Google Play API 事务 (Package: ${packageName})...`);
    const editRes = await publisher.edits.insert({ packageName });
    const editId = editRes.data.id;
    console.log(`   事务创建成功，Edit ID: ${editId}`);

    // 7. 循环更新多国语言 Store Listing
    console.log('\n2. 开始批量更新多语言 Store Listing...');
    let updatedCount = 0;

    for (const [lang, data] of Object.entries(translations)) {
      if (!data || typeof data !== 'object') {
        console.warn(`⚠️ 语言 [${lang}] 数据格式不正确，跳过。`);
        continue;
      }

      const requestBody = {};
      if (data.title && typeof data.title === 'string') requestBody.title = data.title;
      if (data.shortDescription && typeof data.shortDescription === 'string') requestBody.shortDescription = data.shortDescription;
      if (data.fullDescription && typeof data.fullDescription === 'string') requestBody.fullDescription = data.fullDescription;

      if (Object.keys(requestBody).length === 0) {
        console.warn(`⚠️ 语言 [${lang}] 没有包含有效字段 (title, shortDescription, fullDescription)，跳过。`);
        continue;
      }

      try {
        await publisher.edits.listings.update({
          packageName,
          editId,
          language: lang,
          requestBody
        });
        console.log(`   ✅ [${lang}] 已更新 -> ${requestBody.title ? `标题: "${requestBody.title}"` : '更新描述字段'}`);
        updatedCount++;
      } catch (langError) {
        const errMsg = langError.message || '';
        if (errMsg.includes('not currently supported') || (langError.response && langError.response.status === 400)) {
          console.warn(`   ⚠️ [${lang}] 语言不受 Google Play 支持，已自动跳过。`);
        } else {
          console.error(`   ❌ [${lang}] 更新失败: ${errMsg}`);
          if (langError.response && langError.response.data) {
            console.error('   API 错误详情:', JSON.stringify(langError.response.data, null, 2));
          }
        }
      }
    }

    if (updatedCount === 0) {
      console.log('\n⚠️ 没有进行任何有效的语言更新，取消提交事务。');
      return;
    }

    // 8. 提交修改并生效
    console.log('\n3. 提交修改至 Google Play Store...');
    await publisher.edits.commit({ packageName, editId });
    console.log(`\n🎉 成功！所有 Store Listing 更新成功 (共 ${updatedCount} 种语言)！`);

  } catch (error) {
    console.error('\n❌ 更新失败:', error.message);
    if (error.response && error.response.data) {
      console.error('API 详细错误响应:', JSON.stringify(error.response.data, null, 2));
    }
    process.exit(1);
  }
}

main();
