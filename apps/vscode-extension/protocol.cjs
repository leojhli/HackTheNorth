const SIMPLE = new Set(['ready','refresh','connect','capture','retry','ask','explain','practice','end','history','settings','receipt','disconnect']);
function validateMessage(message) {
  if (!message || typeof message!=='object' || Array.isArray(message)) return false;
  if (Object.keys(message).some(k=>!['id','action','payload'].includes(k))) return false;
  if (typeof message.id!=='string' || !/^[a-zA-Z0-9-]{1,80}$/.test(message.id)) return false;
  if (SIMPLE.has(message.action)) return message.payload===undefined;
  if (!['answer','draft'].includes(message.action)) return false;
  const p=message.payload;
  return !!p && typeof p==='object' && !Array.isArray(p) &&
    Object.keys(p).every(k=>['checkpointId','version','snapshotHash','text'].includes(k)) &&
    typeof p.checkpointId==='string' && /^[a-zA-Z0-9-]{1,64}$/.test(p.checkpointId) &&
    Number.isSafeInteger(p.version) && p.version>=1 &&
    typeof p.snapshotHash==='string' && /^[a-f0-9]{64}$/.test(p.snapshotHash) &&
    typeof p.text==='string' && p.text.length<=8000 && (message.action==='draft' || p.text.trim().length>0);
}
module.exports={validateMessage};
