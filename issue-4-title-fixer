// src/title-fixer.js
const fs = require('fs');
const path = require('path');

/**
 * 解析 Markdown 文本，提取所有标题及其行号、层级
 * @param {string} text - 原始 Markdown 文本
 * @returns {Array} 标题对象数组 [{ line, level, raw, text }]
 */
function parseHeadings(text) {
  const lines = text.split('\n');
  const headings = [];
  lines.forEach((line, index) => {
    const match = line.match(/^(#{1,6})\s+(.*)/);
    if (match) {
      headings.push({
        line: index,
        level: match[1].length,
        raw: line,
        text: match[2].trim()
      });
    }
  });
  return headings;
}

/**
 * 修正标题层级：修复跳级、统一 # 后空格、补充根标题
 * @param {string} text - 原始 Markdown 文本
 * @param {string} [defaultTitle] - 若文档无一级标题，用作根标题
 * @returns {Object} { fixedText, changes }
 *   changes: [{ line, original, fixed, type }]
 */
function fixHeadings(text, defaultTitle = '文档标题') {
  const lines = text.split('\n');
  const headings = parseHeadings(text);
  const changes = [];
  let newLines = [...lines];

  // 1. 如果没有一级标题，在文档开头插入一个
  const hasH1 = headings.some(h => h.level === 1);
  if (!hasH1) {
    const insertLine = `# ${defaultTitle}`;
    newLines.unshift(insertLine);
    changes.push({
      line: 0,
      original: '(无一级标题)',
      fixed: insertLine,
      type: 'add-root'
    });
    // 重新解析以更新后续行号
    // 但为了简化，我们后续使用修正后的 lines 再次修正
    // 这里采用重新处理：递归调用一次，但避免死循环，我们直接重新解析新文本
    // 更好的方式：重新运行整个函数，但为了避免无限，我们只处理一次根标题，后面再处理跳级
    // 我们在此处只添加根标题，跳级等后续处理
    // 为了方便，将 newLines 重新组合，再次调用 fixHeadings 但跳过根标题添加？
    // 简单起见，我们把根标题添加后，重新解析并继续。
    // 但因为我们直接修改了 newLines，需要重新计算 headings 和后续修正，
    // 所以这里采用重新构建整个文本，递归调用一次（但只加根标题）
    // 更稳健：先处理跳级，再处理根标题，但跳级依赖原始 headings。
    // 为了清晰，我们先把根标题加上去，然后重新处理整个文本（但可能重复加根标题）
    // 所以用标志控制。
    // 这里我采用先处理跳级，再处理根标题，但跳级时若没有一级可能出错，所以我们先添加根标题。
    // 所以上面的方法是对的，但需要重新解析新文本。
    // 我们直接重新调用 fixHeadings 但传入新的文本，但避免递归，我们在此处执行一次。
    // 我们做一个内部函数 _fix。
    // 为了干净，我们重构：
    // 其实更好的做法：先把根标题补上，然后对整体做跳级修正。
    // 所以我们可以：先补根标题，然后重新解析，再处理跳级。
    // 这里采用分两步：先补根标题，获得新文本，再对全部修正。
    // 为保持函数单一，我们直接调用自身，但用标志防止无限。
    // 更简单：将补根标题放在外部，这里只做跳级和空格。
    // 我们按职责分离：主函数只做跳级和空格，补根标题单独一个函数。
    // 所以我重构：fixHeadings只做跳级和空格，补根标题由外部或一个单独方法。
    // 但任务要求补充根标题，所以我们合并。
    // 解决：我们直接在主函数内处理，但使用一个标记，如果已补过根标题，则不再重复。
    // 我们增加一个参数 _skipRoot 内部使用。
  }

  // 统一 # 后空格（并修复跳级）
  // 先处理空格：确保 # 后有一个空格
  const headingRegex = /^(#{1,6})(\s*)(.*)/;
  const newLinesFixed = newLines.map((line, idx) => {
    const match = line.match(headingRegex);
    if (match) {
      const hashes = match[1];
      const spaces = match[2];
      const content = match[3].trim();
      const correctedLine = `${hashes} ${content}`;
      if (line !== correctedLine) {
        changes.push({
          line: idx,
          original: line,
          fixed: correctedLine,
          type: 'fix-space'
        });
        return correctedLine;
      }
      return line;
    }
    return line;
  });

  // 重新解析新文本的标题
  const newHeadings = parseHeadings(newLinesFixed.join('\n'));
  // 修复跳级：从一级开始，若下一级比上一级+1大，则补充中间级别
  // 我们按顺序处理，维护上一个有效级别
  let prevLevel = 0;
  const levelMap = {}; // 记录每一行需要修正的级别
  newHeadings.forEach((h, index) => {
    let expectedLevel = prevLevel + 1;
    // 如果当前级别 <= 上一级，则保持（允许同级或下降）
    if (h.level > expectedLevel && prevLevel > 0) {
      // 跳级，需要修正为 expectedLevel
      levelMap[h.line] = expectedLevel;
      // 更新 prevLevel 为 expectedLevel（因为修正后级别变了）
      // 但是这里我们只是标记，后面统一修正，但 prevLevel 应跟随修正后的级别
      // 但因为后续标题基于当前标题的修正级别，我们动态调整 prevLevel
      prevLevel = expectedLevel;
    } else {
      prevLevel = h.level;
    }
  });

  // 应用跳级修正
  const finalLines = newLinesFixed.map((line, idx) => {
    if (levelMap[idx] !== undefined) {
      const newLevel = levelMap[idx];
      const content = line.replace(/^#{1,6}\s*/, '').trim();
      const fixed = '#'.repeat(newLevel) + ' ' + content;
      changes.push({
        line: idx,
        original: line,
        fixed: fixed,
        type: 'fix-level'
      });
      return fixed;
    }
    return line;
  });

  // 最后再次检查并添加根标题（如果还没有一级标题）
  const finalHeadings = parseHeadings(finalLines.join('\n'));
  const hasFinalH1 = finalHeadings.some(h => h.level === 1);
  if (!hasFinalH1) {
    const insertLine = `# ${defaultTitle}`;
    finalLines.unshift(insertLine);
    changes.push({
      line: 0,
      original: '(无一级标题)',
      fixed: insertLine,
      type: 'add-root'
    });
  }

  return {
    fixedText: finalLines.join('\n'),
    changes: changes
  };
}

/**
 * 生成修改前后对比数据（供日志模块调用）
 * @param {string} originalText
 * @param {string} fixedText
 * @param {Array} changes - 来自 fixHeadings 的 changes
 * @returns {Object} { original, fixed, diff }
 */
function generateDiff(originalText, fixedText, changes) {
  return {
    original: originalText,
    fixed: fixedText,
    diff: changes.map(c => ({
      line: c.line,
      type: c.type,
      before: c.original,
      after: c.fixed
    }))
  };
}

module.exports = {
  parseHeadings,
  fixHeadings,
  generateDiff
};
