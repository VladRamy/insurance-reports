import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';

const formatValue = (value, type) => {
  if (value === null || value === undefined) return '';
  
  switch (type) {
    case 'currency':
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value);
    case 'percentage':
      return typeof value === 'number' ? `${value.toFixed(2)}%` : value;
    case 'date':
      return new Date(value).toLocaleDateString();
    default:
      return String(value);
  }
};

export const exportToPDF = async ({ title, headers, rows }) => {
  try {
    // Инициализация PDF документа
    const doc = new jsPDF();
    const dateStr = new Date().toLocaleDateString();
    
    // Заголовок отчёта
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(16);
    doc.text(title, 14, 15);
    
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.text(`Generated on ${dateStr}`, 14, 22);
    
    // Подготовка данных для таблицы
    const columns = headers.map(h => ({
      title: h.title,
      dataKey: h.key
    }));
    
    const body = rows.map(row => {
      const formattedRow = {};
      headers.forEach(header => {
        formattedRow[header.key] = formatValue(row[header.key], header.type);
      });
      return formattedRow;
    });
    
    // Добавление таблицы
    autoTable(doc, {
      head: [headers.map(h => h.title)],
      body: body.map(row => headers.map(header => row[header.key])),
      startY: 25,
      margin: { left: 14 },
      headStyles: {
        fillColor: [42, 119, 195],
        textColor: 255,
        fontStyle: 'bold',
        fontSize: 10
      },
      bodyStyles: {
        fontSize: 9,
        cellPadding: 3
      },
      columnStyles: {
        0: { cellWidth: 20 }, // Дата
        1: { cellWidth: 30 }  // Продукт
      },
      didDrawPage: (data) => {
        // Номер страницы в футере
        doc.setFontSize(10);
        doc.text(
          `Page ${data.pageCount}`,
          data.settings.margin.left,
          doc.internal.pageSize.height - 10
        );
      }
    });
    
    // Сохранение файла
    doc.save(`${title.replace(/ /g, '_')}_${dateStr.replace(/\//g, '-')}.pdf`);
    
  } catch (error) {
    console.error('PDF export failed:', error);
    throw new Error('Failed to generate PDF report');
  }
};

export const exportToExcel = async ({ title, headers, rows }) => {
  try {
    const headerTitles = headers.map(h => h.title);
    const data = [
      headerTitles,
      ...rows.map(row => 
        headers.map(header => 
          formatValue(row[header.key], header.type)
        )
      )
    ];
    
    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.aoa_to_sheet(data);
    
    // Настройка ширины столбцов
    ws['!cols'] = headers.map(() => ({ wch: 20 }));
    
    XLSX.utils.book_append_sheet(wb, ws, title.substring(0, 31));
    XLSX.writeFile(wb, `${title.replace(/ /g, '_')}_${new Date().toISOString().slice(0, 10)}.xlsx`);
    
  } catch (error) {
    console.error('Excel export failed:', error);
    throw new Error('Failed to generate Excel report');
  }
};