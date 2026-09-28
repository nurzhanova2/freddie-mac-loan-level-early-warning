#!/usr/bin/env node
/** Audits dissertation links and numbered evidence references without raw data. */
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const languages = ["docs_ru", "docs_en"];
const chapters = [
  "01_research_design_chapter.md", "02_fannie_mae_data_preparation_chapter.md",
  "03_outcomes_features_leakage_chapter.md", "04_models_validation_chapter.md",
  "05_explainability_governance_chapter.md", "06_results_discussion_chapter.md",
];
function references(text, lang) {
  const pattern = lang === "docs_ru"
    ? /(таблиц[аеы]|рисунок|рисунке|рисунках|рисунки|рисунков)\s+([A-ZА-Я]?\.?\d+\.\d+(?:[–-]\d+\.\d+)?)/giu
    : /(tables?|figures?)\s+([A-Z]?\.?\d+\.\d+(?:[–-]\d+\.\d+)?)/giu;
  const result = [];
  for (const match of text.matchAll(pattern)) {
    const kind = /таблиц|table/i.test(match[1]) ? "table" : "figure";
    const range = match[2].replace("–", "-");
    const parts = range.split("-");
    const start = parts[0];
    const end = parts[1];
    result.push(`${kind}:${start}`);
    if (end) {
      const [startChapter] = start.split(".");
      const [endChapter, endIndex] = end.split(".");
      const chapter = endIndex === undefined ? startChapter : endChapter;
      const first = Number(start.split(".")[1]);
      const last = Number(endIndex === undefined ? endChapter : endIndex);
      if (chapter === startChapter && Number.isInteger(first) && Number.isInteger(last) && last >= first && last - first < 20) {
        for (let number = first + 1; number <= last; number += 1) result.push(`${kind}:${chapter}.${number}`);
      } else {
        result.push(`${kind}:${end}`);
      }
    }
  }
  return result;
}
const links = (text, source) => [...text.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)].map((item) => {
  const target = item[1];
  const external = /^(https?:|mailto:|#)/i.test(target);
  return { target, external, exists: external || fs.existsSync(path.resolve(path.dirname(source), target)) };
});

const audit = { generated_at: new Date().toISOString(), languages: {} };
for (const language of languages) {
  const base = path.join(root, "fannie_mae", "docs", language);
  const registered = new Set(references(fs.readFileSync(path.join(base, "appendices", "list_of_tables_and_figures.md"), "utf8"), language));
  const cited = new Set();
  const allLinks = [];
  for (const chapter of chapters) {
    const source = path.join(base, "chapters", chapter);
    const text = fs.readFileSync(source, "utf8");
    references(text, language).forEach((value) => cited.add(value));
    allLinks.push(...links(text, source).map((link) => ({ chapter, ...link })));
  }
  audit.languages[language] = {
    chapter_reference_count: cited.size,
    registered_reference_count: registered.size,
    unregistered_chapter_references: [...cited].filter((value) => !registered.has(value)).sort(),
    missing_local_link_targets: allLinks.filter((link) => !link.external && !link.exists),
    checked_local_link_count: allLinks.filter((link) => !link.external).length,
  };
}
const output = path.join(root, "fannie_mae", "reports", "dissertation_finalization_v01");
fs.mkdirSync(output, { recursive: true });
fs.writeFileSync(path.join(output, "reference_audit_v01.json"), `${JSON.stringify(audit, null, 2)}\n`);
const rows = Object.entries(audit.languages).map(([language, report]) =>
  `| ${language} | ${report.chapter_reference_count} | ${report.registered_reference_count} | ${report.unregistered_chapter_references.length} | ${report.missing_local_link_targets.length} |`);
fs.writeFileSync(path.join(output, "reference_audit_v01.md"), [
  "# Аудит ссылок на таблицы, рисунки и артефакты v01", "",
  "Проверка охватывает шесть основных глав русской и английской версий. Execution reports не входят в нумерацию основной диссертации.", "",
  "| Версия | Ссылок в главах | Номеров в реестре | Незарегистрированные номера | Отсутствующие локальные цели |",
  "|---|---:|---:|---:|---:|", ...rows, "",
  "Полная машинно-читаемая детализация: `reference_audit_v01.json`.", "",
].join("\n"));
