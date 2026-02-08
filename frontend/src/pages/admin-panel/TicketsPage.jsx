import React, { useState, useEffect } from 'react';
import { 
  MessageSquare, Search, Filter, Clock, CheckCircle2, AlertCircle,
  Send, Loader2, User, RefreshCw, X
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const TicketsPage = () => {
  const [tickets, setTickets] = useState([]);
  const [stats, setStats] = useState({ open: 0, pending: 0, closed: 0, urgent: 0 });
  const [loading, setLoading] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [replyText, setReplyText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [filter, setFilter] = useState({ status: '', priority: '', search: '' });

  const token = localStorage.getItem('admin_panel_token');
  const headers = { 'Authorization': `Bearer ${token}` };

  useEffect(() => {
    fetchTickets();
    fetchStats();
  }, [filter.status, filter.priority]);

  const fetchTickets = async () => {
    try {
      let url = `${API_URL}/api/admin-panel/tickets?`;
      if (filter.status) url += `status=${filter.status}&`;
      if (filter.priority) url += `priority=${filter.priority}&`;
      if (filter.search) url += `search=${filter.search}&`;
      
      const response = await fetch(url, { headers });
      if (response.ok) {
        const data = await response.json();
        setTickets(data.tickets);
      }
    } catch (error) {
      toast.error('Failed to fetch tickets');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/admin-panel/tickets/stats`, { headers });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch stats');
    }
  };

  const viewTicket = async (ticketId) => {
    try {
      const response = await fetch(`${API_URL}/api/admin-panel/tickets/${ticketId}`, { headers });
      if (response.ok) {
        const ticket = await response.json();
        setSelectedTicket(ticket);
      }
    } catch (error) {
      toast.error('Failed to load ticket');
    }
  };

  const sendReply = async () => {
    if (!replyText.trim()) return;
    setSubmitting(true);
    
    try {
      const response = await fetch(
        `${API_URL}/api/admin-panel/tickets/${selectedTicket.ticket_id}/reply?message=${encodeURIComponent(replyText)}`,
        { method: 'POST', headers }
      );
      
      if (!response.ok) throw new Error('Failed to send reply');
      
      toast.success('Reply sent!');
      setReplyText('');
      viewTicket(selectedTicket.ticket_id);
      fetchTickets();
    } catch (error) {
      toast.error(error.message);
    } finally {
      setSubmitting(false);
    }
  };

  const updateStatus = async (ticketId, status) => {
    try {
      const response = await fetch(
        `${API_URL}/api/admin-panel/tickets/${ticketId}/status?status=${status}`,
        { method: 'PUT', headers }
      );
      
      if (response.ok) {
        toast.success(`Status updated to ${status}`);
        fetchTickets();
        fetchStats();
        if (selectedTicket?.ticket_id === ticketId) {
          viewTicket(ticketId);
        }
      }
    } catch (error) {
      toast.error('Failed to update status');
    }
  };

  const updatePriority = async (ticketId, priority) => {
    try {
      const response = await fetch(
        `${API_URL}/api/admin-panel/tickets/${ticketId}/priority?priority=${priority}`,
        { method: 'PUT', headers }
      );
      
      if (response.ok) {
        toast.success(`Priority updated to ${priority}`);
        fetchTickets();
        if (selectedTicket?.ticket_id === ticketId) {
          viewTicket(ticketId);
        }
      }
    } catch (error) {
      toast.error('Failed to update priority');
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      open: 'bg-green-500/20 text-green-400',
      pending: 'bg-yellow-500/20 text-yellow-400',
      closed: 'bg-gray-500/20 text-gray-400'
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {status}
      </span>
    );
  };

  const getPriorityBadge = (priority) => {
    const styles = {
      low: 'text-gray-400',
      normal: 'text-blue-400',
      high: 'text-orange-400',
      urgent: 'text-red-400 font-bold'
    };
    return <span className={`text-xs ${styles[priority]}`}>{priority}</span>;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Support Tickets</h1>
          <p className="text-white/50 mt-1">Manage customer support requests</p>
        </div>
        <button
          onClick={() => { fetchTickets(); fetchStats(); }}
          className="p-2 text-white/60 hover:text-white hover:bg-white/5 rounded-lg"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-xl">
          <p className="text-green-400 text-sm">Open</p>
          <p className="text-2xl font-bold text-white">{stats.open}</p>
        </div>
        <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-xl">
          <p className="text-yellow-400 text-sm">Pending</p>
          <p className="text-2xl font-bold text-white">{stats.pending}</p>
        </div>
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
          <p className="text-red-400 text-sm">Urgent</p>
          <p className="text-2xl font-bold text-white">{stats.urgent}</p>
        </div>
        <div className="p-4 bg-gray-500/10 border border-gray-500/20 rounded-xl">
          <p className="text-gray-400 text-sm">Closed</p>
          <p className="text-2xl font-bold text-white">{stats.closed}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30" />
          <input
            type="text"
            placeholder="Search tickets..."
            value={filter.search}
            onChange={(e) => setFilter({ ...filter, search: e.target.value })}
            onKeyDown={(e) => e.key === 'Enter' && fetchTickets()}
            className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/30 focus:border-indigo-500 focus:outline-none"
          />
        </div>
        <select
          value={filter.status}
          onChange={(e) => setFilter({ ...filter, status: e.target.value })}
          className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none"
        >
          <option value="">All Status</option>
          <option value="open">Open</option>
          <option value="pending">Pending</option>
          <option value="closed">Closed</option>
        </select>
        <select
          value={filter.priority}
          onChange={(e) => setFilter({ ...filter, priority: e.target.value })}
          className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none"
        >
          <option value="">All Priority</option>
          <option value="urgent">Urgent</option>
          <option value="high">High</option>
          <option value="normal">Normal</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Ticket List & Detail */}
      <div className="grid grid-cols-3 gap-6">
        {/* List */}
        <div className="col-span-1 space-y-2 max-h-[600px] overflow-y-auto">
          {loading ? (
            <div className="text-center py-10">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-500 mx-auto" />
            </div>
          ) : tickets.length === 0 ? (
            <div className="text-center py-10 text-white/50">
              No tickets found
            </div>
          ) : (
            tickets.map((ticket) => (
              <button
                key={ticket.ticket_id}
                onClick={() => viewTicket(ticket.ticket_id)}
                className={`w-full p-4 rounded-xl text-left transition-all ${
                  selectedTicket?.ticket_id === ticket.ticket_id
                    ? 'bg-indigo-500/20 border border-indigo-500/30'
                    : 'bg-white/5 border border-white/5 hover:bg-white/10'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-white/40 text-xs">{ticket.ticket_id}</span>
                  {getStatusBadge(ticket.status)}
                </div>
                <h3 className="font-medium text-white truncate">{ticket.subject}</h3>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-white/50 text-xs">{ticket.user_email}</span>
                  {getPriorityBadge(ticket.priority)}
                </div>
              </button>
            ))
          )}
        </div>

        {/* Detail */}
        <div className="col-span-2">
          {selectedTicket ? (
            <div className="bg-[#1e293b] rounded-xl border border-white/10 overflow-hidden">
              <div className="p-5 border-b border-white/10">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-white/40">{selectedTicket.ticket_id}</span>
                      {getStatusBadge(selectedTicket.status)}
                      {getPriorityBadge(selectedTicket.priority)}
                    </div>
                    <h2 className="text-xl font-bold text-white">{selectedTicket.subject}</h2>
                    <p className="text-white/50 text-sm mt-1">
                      {selectedTicket.user_name} ({selectedTicket.user_email})
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectedTicket(null)}
                    className="p-2 text-white/50 hover:text-white"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
                
                {/* Actions */}
                <div className="flex gap-2 mt-4">
                  <select
                    value={selectedTicket.status}
                    onChange={(e) => updateStatus(selectedTicket.ticket_id, e.target.value)}
                    className="px-3 py-1.5 bg-white/5 border border-white/10 rounded text-white text-sm"
                  >
                    <option value="open">Open</option>
                    <option value="pending">Pending</option>
                    <option value="closed">Closed</option>
                  </select>
                  <select
                    value={selectedTicket.priority}
                    onChange={(e) => updatePriority(selectedTicket.ticket_id, e.target.value)}
                    className="px-3 py-1.5 bg-white/5 border border-white/10 rounded text-white text-sm"
                  >
                    <option value="low">Low</option>
                    <option value="normal">Normal</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
              </div>

              {/* Messages */}
              <div className="p-5 space-y-4 max-h-80 overflow-y-auto">
                {selectedTicket.messages?.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`p-4 rounded-xl ${
                      msg.sender_type === 'admin'
                        ? 'bg-indigo-500/10 border border-indigo-500/20 ml-8'
                        : 'bg-white/5 mr-8'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <User className="w-4 h-4 text-white/40" />
                      <span className={`font-medium ${msg.sender_type === 'admin' ? 'text-indigo-400' : 'text-white'}`}>
                        {msg.sender_name}
                      </span>
                      <span className="text-white/30 text-xs">
                        {new Date(msg.created_at).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-white/80 whitespace-pre-wrap">{msg.message}</p>
                  </div>
                ))}
              </div>

              {/* Reply */}
              {selectedTicket.status !== 'closed' && (
                <div className="p-5 border-t border-white/10">
                  <div className="flex gap-3">
                    <textarea
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      placeholder="Type your reply..."
                      className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/30 min-h-[80px] focus:outline-none focus:border-indigo-500"
                    />
                    <button
                      onClick={sendReply}
                      disabled={submitting || !replyText.trim()}
                      className="px-6 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 disabled:opacity-50"
                    >
                      {submitting ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-[#1e293b] rounded-xl border border-white/10 flex items-center justify-center h-96">
              <div className="text-center text-white/40">
                <MessageSquare className="w-12 h-12 mx-auto mb-3" />
                <p>Select a ticket to view details</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TicketsPage;
