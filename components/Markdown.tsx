import React from 'react';

interface MarkdownProps {
  content: string;
}

/**
 * Lightweight Markdown renderer tailored for the official documents
 * (ETP / DFD / TR). Handles headings, bold, ordered/unordered lists,
 * GFM tables, horizontal rules and paragraphs — enough for clean
 * on-screen rendering and html2pdf/DOCX export.
 */
const renderInline = (text: string): React.ReactNode => {
  // Split on **bold** segments, keeping delimiters.
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return <React.Fragment key={i}>{part}</React.Fragment>;
  });
};

const Markdown: React.FC<MarkdownProps> = ({ content }) => {
  const lines = content.replace(/\r\n/g, '\n').split('\n');
  const blocks: React.ReactNode[] = [];

  let i = 0;
  let key = 0;

  const isTableRow = (l: string) => /^\s*\|.*\|\s*$/.test(l);

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    // Blank line
    if (trimmed === '') {
      i++;
      continue;
    }

    // Horizontal rule
    if (/^(-{3,}|_{3,}|\*{3,})$/.test(trimmed)) {
      blocks.push(<hr key={key++} className="my-4 border-slate-300" />);
      i++;
      continue;
    }

    // Headings
    const headingMatch = trimmed.match(/^(#{1,4})\s+(.*)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const txt = headingMatch[2].replace(/\*\*/g, '');
      if (level === 1) {
        blocks.push(
          <h1 key={key++} className="text-xl font-bold text-slate-900 uppercase text-center mb-4 mt-2 tracking-tight">
            {txt}
          </h1>
        );
      } else if (level === 2) {
        blocks.push(
          <h2 key={key++} className="text-sm font-bold text-slate-900 uppercase border-b border-slate-300 pb-1 mb-3 mt-6">
            {txt}
          </h2>
        );
      } else {
        blocks.push(
          <h3 key={key++} className="text-sm font-semibold text-slate-800 mb-2 mt-4">
            {txt}
          </h3>
        );
      }
      i++;
      continue;
    }

    // Tables (GFM)
    if (isTableRow(line) && i + 1 < lines.length && /^\s*\|?[\s:|-]+\|?\s*$/.test(lines[i + 1])) {
      const headerCells = line.split('|').slice(1, -1).map((c) => c.trim());
      i += 2; // skip header + separator
      const rows: string[][] = [];
      while (i < lines.length && isTableRow(lines[i])) {
        rows.push(lines[i].split('|').slice(1, -1).map((c) => c.trim()));
        i++;
      }
      blocks.push(
        <div key={key++} className="overflow-x-auto my-4">
          <table className="min-w-full text-xs border border-slate-300 border-collapse">
            <thead className="bg-slate-100">
              <tr>
                {headerCells.map((c, idx) => (
                  <th key={idx} className="border border-slate-300 px-3 py-2 text-left font-semibold text-slate-700">
                    {renderInline(c)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, ri) => (
                <tr key={ri} className={ri % 2 ? 'bg-slate-50' : 'bg-white'}>
                  {r.map((c, ci) => (
                    <td key={ci} className="border border-slate-300 px-3 py-2 text-slate-700 align-top">
                      {renderInline(c)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      continue;
    }

    // Ordered list
    if (/^\d+\.\s+/.test(trimmed)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*\d+\.\s+/, ''));
        i++;
      }
      blocks.push(
        <ol key={key++} className="list-decimal pl-6 mb-3 space-y-1 text-sm text-slate-700 text-justify">
          {items.map((it, idx) => (
            <li key={idx}>{renderInline(it)}</li>
          ))}
        </ol>
      );
      continue;
    }

    // Unordered list
    if (/^[-*]\s+/.test(trimmed)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*]\s+/, ''));
        i++;
      }
      blocks.push(
        <ul key={key++} className="list-disc pl-6 mb-3 space-y-1 text-sm text-slate-700 text-justify">
          {items.map((it, idx) => (
            <li key={idx}>{renderInline(it)}</li>
          ))}
        </ul>
      );
      continue;
    }

    // Paragraph (collect consecutive non-empty, non-special lines)
    const paragraph: string[] = [];
    while (
      i < lines.length &&
      lines[i].trim() !== '' &&
      !/^(#{1,4})\s+/.test(lines[i].trim()) &&
      !/^[-*]\s+/.test(lines[i].trim()) &&
      !/^\d+\.\s+/.test(lines[i].trim()) &&
      !isTableRow(lines[i]) &&
      !/^(-{3,}|_{3,}|\*{3,})$/.test(lines[i].trim())
    ) {
      paragraph.push(lines[i].trim());
      i++;
    }
    blocks.push(
      <p key={key++} className="text-sm text-slate-700 leading-relaxed text-justify mb-3">
        {renderInline(paragraph.join(' '))}
      </p>
    );
  }

  return <>{blocks}</>;
};

export default Markdown;
