// 209 Adaptation Cycle — GA4 → decision → Supabase
// Set env: SUPABASE_URL, SUPABASE_SERVICE_KEY, GA4_PROPERTY_ID, GA4_CREDENTIALS
require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');
const { BetaAnalyticsDataClient } = require('@google-analytics/data');
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);
const ga4 = new BetaAnalyticsDataClient({ credentials: JSON.parse(process.env.GA4_CREDENTIALS) });
async function topPosts() {
  const [res] = await ga4.runReport({
    property: `properties/${process.env.GA4_PROPERTY_ID}`,
    dateRanges: [{ startDate: '2daysAgo', endDate: 'today' }],
    dimensions: [{ name: 'pageTitle' }, { name: 'pagePath' }],
    metrics: [{ name: 'engagementRate' }, { name: 'activeUsers' }],
    orderBy: [{ metric: { metricName: 'activeUsers' }, desc: true }],
    limit: 5
  });
  return res.rows || [];
}
async function writeTopPosts(rows) {
  for (const r of rows) {
    await supabase.from('top_posts_48h').insert({
      title: r.dimensionValues[0].value,
      platform: 'Web',
      engagement_delta: parseFloat(r.metricValues[0].value) * 100,
      reason: 'Top engagement last 48h',
      url: r.dimensionValues[1].value
    });
  }
}
async function writeDecision() {
  await supabase.from('adaptation_log').insert({
    trigger: 'Scheduled cycle',
    observation: 'Reviewed top posts and engagement trends',
    decision: 'Maintain current hook strategy',
    action: 'No change needed this cycle',
    status: 'Applied',
    platform: 'All'
  });
}
(async () => {
  const rows = await topPosts();
  await writeTopPosts(rows);
  await writeDecision();
  console.log('Adaptation cycle complete');
})();