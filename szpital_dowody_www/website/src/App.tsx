import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface TimelineEvent {
  date: string;
  title: string;
  status: string;
  facts: string[];
  content: string;
}

interface PersonnelData {
  sections: { title: string; body: string }[];
  content: string;
}

interface EvidenceDoc {
  filename: string;
  content: string;
}

interface AppData {
  timeline: TimelineEvent[];
  personnel: PersonnelData;
  evidence: EvidenceDoc[];
}

function App() {
  const [data, setData] = useState<AppData | null>(null);
  const [activeTab, setActiveTab] = useState<'timeline' | 'personnel' | 'evidence'>('timeline');
  const [selectedDay, setSelectedDay] = useState<TimelineEvent | null>(null);

  useEffect(() => {
    fetch('/data.json')
      .then(res => res.json())
      .then(setData);
  }, []);

  if (!data) return <div className="p-10 text-center text-xl text-white">Ładowanie danych...</div>;

  return (
    <div className="min-h-screen font-sans text-gray-100 bg-gray-900">
      <header className="bg-red-900 text-white p-6 shadow-lg border-b-4 border-red-700">
        <h1 className="text-4xl font-bold uppercase tracking-widest text-center">Dowody Zaniedbań Szpitalnych</h1>
        <p className="text-center mt-2 text-red-200">Dokumentacja dzień po dniu & lista odpowiedzialnych</p>
      </header>

      <nav className="flex justify-center bg-gray-800 p-4 sticky top-0 z-50 shadow-md flex-wrap gap-2">
        <button
          onClick={() => setActiveTab('timeline')}
          className={`px-6 py-2 font-bold rounded ${activeTab === 'timeline' ? 'bg-red-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
        >
          OS CZASU (DZIEŃ PO DNIU)
        </button>
        <button
          onClick={() => setActiveTab('personnel')}
          className={`px-6 py-2 font-bold rounded ${activeTab === 'personnel' ? 'bg-red-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
        >
          PERSONEL / ODPOWIEDZIALNI
        </button>
        <button
          onClick={() => setActiveTab('evidence')}
          className={`px-6 py-2 font-bold rounded ${activeTab === 'evidence' ? 'bg-red-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
        >
          KLUCZOWE DOWODY
        </button>
      </nav>

      <main className="container mx-auto p-4">
        {activeTab === 'timeline' && (
          <div className="flex flex-col md:flex-row gap-6">
            <div className="md:w-1/3 overflow-y-auto h-[80vh] border-r border-gray-700 pr-4 space-y-2">
              {data.timeline.map((day, idx) => (
                <div
                  key={idx}
                  onClick={() => setSelectedDay(day)}
                  className={`p-4 cursor-pointer rounded border transition-all ${selectedDay === day ? 'bg-red-900/50 border-red-500' : 'bg-gray-800 border-gray-700 hover:bg-gray-700'}`}
                >
                  <div className="font-bold text-red-400">{day.date}</div>
                  <div className="font-semibold text-sm">{day.title}</div>
                  {day.status && <div className="text-xs text-gray-400 mt-1">{day.status}</div>}
                </div>
              ))}
            </div>
            <div className="md:w-2/3 bg-gray-800 p-6 rounded border border-gray-700 h-[80vh] overflow-y-auto">
              {selectedDay ? (
                <article className="prose prose-invert max-w-none">
                  <h2 className="text-3xl font-bold text-red-500 mb-4">{selectedDay.title}</h2>
                  <p className="text-xl text-gray-300 mb-6">{selectedDay.status}</p>

                  {selectedDay.facts.length > 0 && (
                    <div className="bg-red-900/20 border-l-4 border-red-600 p-4 mb-6">
                      <h3 className="text-red-400 font-bold mb-2 text-lg">KLUCZOWE FAKTY:</h3>
                      <ul className="list-disc list-inside space-y-1">
                        {selectedDay.facts.map((fact, i) => <li key={i}>{fact}</li>)}
                      </ul>
                    </div>
                  )}

                  <div className="markdown-content">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{selectedDay.content}</ReactMarkdown>
                  </div>
                </article>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500 text-xl">
                  Wybierz dzień z listy po lewej
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'personnel' && (
          <div className="bg-gray-800 p-8 rounded border border-gray-700">
            <h2 className="text-3xl font-bold text-red-600 mb-6 border-b border-gray-700 pb-2">PERSONEL I KOMUNIKACJA ("LISTA OPRAWCÓW")</h2>

             <article className="prose prose-invert max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{data.personnel.content}</ReactMarkdown>
             </article>
          </div>
        )}

        {activeTab === 'evidence' && (
          <div className="space-y-8">
            {data.evidence.map((doc, idx) => (
              <div key={idx} className="bg-gray-800 p-8 rounded border border-gray-700">
                 <h3 className="text-2xl font-bold text-red-500 mb-4">{doc.filename.replace(/_/g, ' ').replace('.md', '')}</h3>
                 <div className="overflow-y-auto bg-gray-900 p-4 rounded border border-gray-700 max-h-[800px]">
                   <article className="prose prose-invert max-w-none">
                     <ReactMarkdown remarkPlugins={[remarkGfm]}>{doc.content}</ReactMarkdown>
                   </article>
                 </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
