import { useState } from 'react';
import { Download, Loader2, Video, AlertCircle, Sparkles, Shield, Zap, Globe, ChevronDown, ChevronUp } from 'lucide-react';

interface FormatOption {
  label: string;
  quality: string;
  ext: string;
  format_id: string;
  height: number;
  tbr: number;
  url: string;
  proxy_url?: string;
  media_type: 'combined' | 'video' | 'audio';
}

interface VideoResult {
  title: string;
  thumbnail?: string;
  duration?: string;
  downloadUrl: string;
  format: string;
  quality: string;
  formats?: FormatOption[];
  selectedFormatId?: string;
}

interface FAQItem {
  question: string;
  answer: string;
}

const faqItems: FAQItem[] = [
  {
    question: "Is KGDownloader free to use?",
    answer: "Yes, KGDownloader is completely free to use. There are no hidden charges, subscriptions, or premium plans. You can download unlimited videos from Instagram, TikTok, YouTube, Facebook, and Twitter without paying anything."
  },
  {
    question: "Does KGDownloader support HD video downloads?",
    answer: "Absolutely! KGDownloader supports high-quality video downloads including HD and Full HD formats. We automatically fetch the best available quality from the source platform, ensuring you get crystal-clear videos."
  },
  {
    question: "Do I need to create an account to use KGDownloader?",
    answer: "No account or registration is required. Simply paste the video URL and download instantly. We value your privacy and don't collect any personal information. No sign-up, no login, just fast downloads."
  },
  {
    question: "Is KGDownloader safe and secure?",
    answer: "Yes, KGDownloader is 100% safe and secure. We don't store any videos on our servers. All downloads are processed directly from the source platform. We use secure connections and don't require any dangerous permissions."
  },
  {
    question: "Does KGDownloader add watermarks to downloaded videos?",
    answer: "No, KGDownloader never adds watermarks to your downloaded videos. You get the original video content exactly as it appears on the source platform, without any logos, watermarks, or modifications."
  },
  {
    question: "Which platforms are supported by KGDownloader?",
    answer: "KGDownloader supports over 1000+ platforms including Instagram (Reels, Stories, Posts), TikTok, YouTube (Videos, Shorts), Facebook, Twitter/X, Vimeo, Dailymotion, and many more social media and video sharing sites."
  }
];

function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<VideoResult | null>(null);
  const [selectedFormatId, setSelectedFormatId] = useState<string | null>(null);
  const [openFaqIndex, setOpenFaqIndex] = useState<number | null>(null);

  const apiUrl = import.meta.env.VITE_API_URL || '';

  const handleFormatChange = (formatId: string) => {
    if (!result?.formats) {
      return;
    }

    const selected = result.formats.find((fmt) => fmt.format_id === formatId);
    if (!selected) {
      return;
    }

    const downloadUrl = selected.url
      ? selected.url
      : selected.proxy_url
        ? `${apiUrl}${selected.proxy_url}`
        : '';
    setSelectedFormatId(formatId);
    setResult({ ...result, downloadUrl, quality: selected.label, selectedFormatId: formatId });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!url.trim()) {
      setError('Please enter a valid URL');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${apiUrl}/api/download`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url.trim(),
          format_id: selectedFormatId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to fetch video information');
      }

      const data = await response.json();

      if (!data.download_url) {
        throw new Error('No downloadable content found');
      }

      const downloadUrl = data.download_url && data.download_url.startsWith('/api/')
        ? `${apiUrl}${data.download_url}`
        : data.download_url;

      const formats = data.formats || [];
      const initialFormatId = data.selected_format_id || formats[0]?.format_id || null;
      setSelectedFormatId(initialFormatId);
      setResult({
        title: data.title || 'Video',
        thumbnail: data.thumbnail,
        duration: data.duration,
        downloadUrl,
        format: data.format || 'mp4',
        quality: data.quality || 'best',
        formats,
        selectedFormatId: initialFormatId,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (downloadUrl: string) => {
    window.open(downloadUrl, '_blank', 'noopener,noreferrer');
  };

  const selectedFormat = result?.formats?.find((fmt) => fmt.format_id === selectedFormatId) || result?.formats?.[0];
  const combinedFormats = result?.formats?.filter((fmt) => fmt.media_type === 'combined') || [];
  const videoOnlyFormats = result?.formats?.filter((fmt) => fmt.media_type === 'video') || [];
  const audioOnlyFormats = result?.formats?.filter((fmt) => fmt.media_type === 'audio') || [];

  const downloadButtonText = selectedFormat
    ? selectedFormat.media_type === 'audio'
      ? `Download ${selectedFormat.label}`
      : selectedFormat.media_type === 'video'
        ? `Download ${selectedFormat.label} (video only)`
        : `Download ${selectedFormat.label}`
    : 'Download MP4';

  const selectedFormatDescription = selectedFormat
    ? selectedFormat.media_type === 'audio'
      ? 'Audio only file. Use this for editing or adding sound later.'
      : selectedFormat.media_type === 'video'
        ? 'Video only file. No audio included.'
        : 'Video + audio file.'
    : '';

  return (
    <div className="min-h-screen bg-gradient-dark">
      {/* Top Ad Placeholder */}
      <aside className="ad-placeholder h-20 mx-4 mt-4 md:mx-8 md:mt-6" aria-label="Advertisement">
        Advertisement Space
      </aside>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-12 md:py-20">
        {/* Hero Section */}
        <header className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-primary-500/10 border border-primary-500/20 rounded-full px-4 py-2 mb-6">
            <Sparkles className="w-4 h-4 text-primary-400" aria-hidden="true" />
            <span className="text-sm text-primary-300">Fast & Free Video Downloads</span>
          </div>

          <h1 className="text-4xl md:text-6xl font-bold mb-4">
            <span className="text-white">KG</span>
            <span className="text-gradient">Downloader</span>
          </h1>

          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Download high-quality videos, reels, and shorts from Instagram, TikTok, YouTube,
            Facebook, and Twitter for free. Fast, safe, and no watermark.
          </p>
        </header>

        {/* Download Form */}
        <section aria-labelledby="download-heading">
          <h2 id="download-heading" className="sr-only">Video Download Form</h2>
          <div className="card p-6 md:p-8 glow mb-8">
            <form onSubmit={handleSubmit} className="space-y-4" role="form">
              <label htmlFor="video-url" className="sr-only">Video URL</label>
              <div className="flex flex-col md:flex-row gap-4">
                <input
                  id="video-url"
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="Paste your video URL here..."
                  className="input-field flex-1"
                  disabled={loading}
                  aria-describedby="supported-platforms"
                  autoComplete="url"
                />
                <button
                  type="submit"
                  className="btn-primary flex items-center justify-center gap-2 min-w-[160px]"
                  disabled={loading}
                  aria-busy={loading}
                  aria-label={loading ? 'Fetching video information' : 'Download video'}
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />
                      <span>Fetching...</span>
                    </>
                  ) : (
                    <>
                      <Download className="w-5 h-5" aria-hidden="true" />
                      <span>Download</span>
                    </>
                  )}
                </button>
              </div>
            </form>

            {/* Supported Platforms */}
            <div id="supported-platforms" className="mt-6" aria-label="Supported platforms">
              <p className="sr-only">Video Downloader supports the following platforms:</p>
              <div className="flex flex-wrap justify-center gap-3 text-xs text-gray-500">
                <span className="bg-dark-300/50 px-3 py-1 rounded-full">YouTube</span>
                <span className="bg-dark-300/50 px-3 py-1 rounded-full">TikTok</span>
                <span className="bg-dark-300/50 px-3 py-1 rounded-full">Instagram</span>
                <span className="bg-dark-300/50 px-3 py-1 rounded-full">Facebook</span>
                <span className="bg-dark-300/50 px-3 py-1 rounded-full">Twitter</span>
                <span className="bg-dark-300/50 px-3 py-1 rounded-full">And More</span>
              </div>
            </div>
          </div>
        </section>

        {/* Error Message */}
        {error && (
          <div className="card p-4 mb-6 border-red-500/30 bg-red-500/5" role="alert" aria-live="assertive">
            <div className="flex items-center gap-3 text-red-400">
              <AlertCircle className="w-5 h-5 flex-shrink-0" aria-hidden="true" />
              <span>{error}</span>
            </div>
          </div>
        )}

        {/* Results */}
        {result && (
          <section aria-labelledby="result-heading" className="card p-6 md:p-8 glow animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h2 id="result-heading" className="sr-only">Video Download Ready</h2>
            <div className="flex flex-col md:flex-row gap-6 mb-6">
              {result.thumbnail && (
                <div className="flex-shrink-0">
                  <img
                    src={result.thumbnail}
                    alt={`Thumbnail for ${result.title}`}
                    className="w-full md:w-48 h-32 object-cover rounded-lg"
                    loading="lazy"
                  />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <h3 className="text-xl font-semibold text-white mb-2 line-clamp-2">
                  {result.title}
                </h3>
                <div className="flex flex-col gap-4 text-sm text-gray-500 mb-4">
                  <div className="flex flex-wrap items-center gap-4">
                    <div className="flex items-center gap-2">
                      <Video className="w-4 h-4" aria-hidden="true" />
                      <span>{result.format.toUpperCase()} - {result.quality}</span>
                    </div>
                    {result.duration && (
                      <span>Duration: {result.duration}</span>
                    )}
                  </div>

                  {result.formats && result.formats.length > 0 && (
                    <div className="flex flex-col gap-4">
                      <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-gray-400 mb-2">Video + Audio</p>
                        <div className="grid grid-cols-3 gap-2 mb-3">
                          {combinedFormats.map((format) => (
                            <button
                              key={format.format_id}
                              type="button"
                              onClick={() => handleFormatChange(format.format_id)}
                              className={`rounded-lg border px-3 py-2 text-xs font-semibold transition ${selectedFormatId === format.format_id ? 'border-primary-500 bg-primary-500/10 text-white' : 'border-gray-700 bg-dark-300 text-gray-300 hover:border-primary-500 hover:text-white'}`}
                            >
                              {format.label}
                            </button>
                          ))}
                        </div>
                      </div>

                      <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-gray-400 mb-2">Video Only</p>
                        <div className="grid grid-cols-3 gap-2 mb-3">
                          {videoOnlyFormats.map((format) => (
                            <button
                              key={format.format_id}
                              type="button"
                              onClick={() => handleFormatChange(format.format_id)}
                              className={`rounded-lg border px-3 py-2 text-xs font-semibold transition ${selectedFormatId === format.format_id ? 'border-primary-500 bg-primary-500/10 text-white' : 'border-gray-700 bg-dark-300 text-gray-300 hover:border-primary-500 hover:text-white'}`}
                            >
                              {format.label}
                            </button>
                          ))}
                        </div>
                      </div>

                      <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-gray-400 mb-2">Audio Only</p>
                        <div className="grid grid-cols-3 gap-2">
                          {audioOnlyFormats.map((format) => (
                            <button
                              key={format.format_id}
                              type="button"
                              onClick={() => handleFormatChange(format.format_id)}
                              className={`rounded-lg border px-3 py-2 text-xs font-semibold transition ${selectedFormatId === format.format_id ? 'border-primary-500 bg-primary-500/10 text-white' : 'border-gray-700 bg-dark-300 text-gray-300 hover:border-primary-500 hover:text-white'}`}
                            >
                              {format.label}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                  {selectedFormatDescription && (
                    <p className="text-xs text-gray-400">{selectedFormatDescription}</p>
                  )}
                </div>
                <button
                  onClick={() => handleDownload(result.downloadUrl)}
                  className="btn-primary flex items-center gap-2 w-full sm:w-auto justify-center"
                  aria-label={downloadButtonText}
                >
                  <Download className="w-5 h-5" aria-hidden="true" />
                  <span>{downloadButtonText}</span>
                </button>
              </div>
            </div>
          </section>
        )}

        {/* Features Section */}
        <section aria-labelledby="features-heading" className="mt-16">
          <h2 id="features-heading" className="text-center text-2xl font-bold text-white mb-8">
            Why Choose KGDownloader?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <article className="card p-6 text-center">
              <div className="bg-primary-500/10 w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Zap className="w-6 h-6 text-primary-400" aria-hidden="true" />
              </div>
              <h3 className="font-semibold text-white mb-2">Fast Downloads</h3>
              <p className="text-sm text-gray-400">Get your videos in seconds with our optimized servers</p>
            </article>
            <article className="card p-6 text-center">
              <div className="bg-primary-500/10 w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Shield className="w-6 h-6 text-primary-400" aria-hidden="true" />
              </div>
              <h3 className="font-semibold text-white mb-2">No Watermark</h3>
              <p className="text-sm text-gray-400">Download original videos without any watermarks or logos</p>
            </article>
            <article className="card p-6 text-center">
              <div className="bg-primary-500/10 w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Globe className="w-6 h-6 text-primary-400" aria-hidden="true" />
              </div>
              <h3 className="font-semibold text-white mb-2">All Platforms</h3>
              <p className="text-sm text-gray-400">Works with YouTube, TikTok, Instagram, Facebook, Twitter</p>
            </article>
          </div>
        </section>

        {/* FAQ Section */}
        <section aria-labelledby="faq-heading" className="mt-16">
          <h2 id="faq-heading" className="text-center text-2xl font-bold text-white mb-8">
            Frequently Asked Questions
          </h2>
          <div className="space-y-4">
            {faqItems.map((faq, index) => (
              <div key={index} className="card overflow-hidden">
                <button
                  onClick={() => toggleFaq(index)}
                  className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-dark-300/20 transition-colors"
                  aria-expanded={openFaqIndex === index}
                  aria-controls={"faq-answer-" + index}
                  id={"faq-question-" + index}
                >
                  <span className="font-medium text-white pr-4">{faq.question}</span>
                  {openFaqIndex === index ? (
                    <ChevronUp className="w-5 h-5 text-primary-400 flex-shrink-0" aria-hidden="true" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" aria-hidden="true" />
                  )}
                </button>
                <div
                  id={"faq-answer-" + index}
                  className={"overflow-hidden transition-all duration-300 " + (openFaqIndex === index ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0')}
                  role="region"
                  aria-labelledby={"faq-question-" + index}
                >
                  <p className="px-6 pb-4 text-gray-400">{faq.answer}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* How to Use Section */}
        <section aria-labelledby="howto-heading" className="mt-16">
          <h2 id="howto-heading" className="text-center text-2xl font-bold text-white mb-8">
            How to Use KGDownloader
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <article className="card p-6 text-center">
              <div className="bg-primary-500/20 w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-primary-400 font-bold">1</span>
              </div>
              <h3 className="font-semibold text-white mb-2">Copy Video URL</h3>
              <p className="text-sm text-gray-400">Copy the video link from Instagram, TikTok, YouTube, or any supported platform</p>
            </article>
            <article className="card p-6 text-center">
              <div className="bg-primary-500/20 w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-primary-400 font-bold">2</span>
              </div>
              <h3 className="font-semibold text-white mb-2">Paste & Click Download</h3>
              <p className="text-sm text-gray-400">Paste the URL in the input box above and click the Download button</p>
            </article>
            <article className="card p-6 text-center">
              <div className="bg-primary-500/20 w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-primary-400 font-bold">3</span>
              </div>
              <h3 className="font-semibold text-white mb-2">Download Your Video</h3>
              <p className="text-sm text-gray-400">Click the download link and save the video to your device instantly</p>
            </article>
          </div>
        </section>
      </main>

      {/* Bottom Ad Placeholder */}
      <aside className="ad-placeholder h-24 mx-4 mb-4 md:mx-8 md:mb-6" aria-label="Advertisement">
        Advertisement Space
      </aside>

      {/* Footer */}
      <footer className="text-center py-8 text-gray-500 text-sm border-t border-dark-100/20">
        <p>KGDownloader - Free Video Downloader for Instagram, TikTok, YouTube, Facebook, Twitter</p>
        <p className="mt-2 text-xs text-gray-600">
          Fast, Safe, and No Watermark | 1000+ Platforms Supported
        </p>
      </footer>

    </div>
  );
}

export default App;
