package raft

//
// Raft tests.
//
// we will use the original test_test.go to test your code for grading.
// so, while you can modify this code to help you debug, please
// test with the original before submitting.
//

import "testing"
import "fmt"
import "time"
import "math/rand"
// import "sync/atomic"
import "sync"

// The tester generously allows solutions to complete elections in one second
// (much more than the paper's range of timeouts).
const RaftElectionTimeout = 1000 * time.Millisecond

func TestInitialElection(t *testing.T) {
	servers := 3
	cfg := make_config(t, servers, false)
	defer cfg.cleanup()

	fmt.Printf("Test: initial election ...\n")

	// is a leader elected?
	cfg.checkOneLeader()

	// does the leader+term stay the same there is no failure?
	term1 := cfg.checkTerms()
	time.Sleep(2 * RaftElectionTimeout)
	term2 := cfg.checkTerms()
	if term1 != term2 {
		fmt.Printf("warning: term changed even though there were no failures")
	}

	fmt.Printf("  ... Passed\n")
}

func TestReElection(t *testing.T) {
	servers := 3
	cfg := make_config(t, servers, false)
	defer cfg.cleanup()

	fmt.Printf("Test: election after network failure ...\n")

	leader1 := cfg.checkOneLeader()

	// if the leader disconnects, a new one should be elected.
	cfg.disconnect(leader1)
	cfg.checkOneLeader()

	// if the old leader rejoins, that shouldn't
	// disturb the old leader.
	cfg.connect(leader1)
	leader2 := cfg.checkOneLeader()

	// if there's no quorum, no leader should
	// be elected.
	cfg.disconnect(leader2)
	cfg.disconnect((leader2 + 1) % servers)
	time.Sleep(2 * RaftElectionTimeout)
	cfg.checkNoLeader()

	// if a quorum arises, it should elect a leader.
	cfg.connect((leader2 + 1) % servers)
	cfg.checkOneLeader()

	// re-join of last node shouldn't prevent leader from existing.
	cfg.connect(leader2)
	cfg.checkOneLeader()

	fmt.Printf("  ... Passed\n")
}

func TestBasicAgree(t *testing.T) {
	servers := 5
	cfg := make_config(t, servers, false)
	defer cfg.cleanup()

	fmt.Printf("Test: basic agreement ...\n")

	iters := 3
	for index := 1; index < iters+1; index++ {
		nd, _ := cfg.nCommitted(index)
		if nd > 0 {
			t.Fatalf("some have committed before Start()")
		}

		xindex := cfg.one(index*100, servers)
		if xindex != index {
			t.Fatalf("got index %v but expected %v", xindex, index)
		}
	}

	fmt.Printf("  ... Passed\n")
}

func TestFailAgree(t *testing.T) {
	servers := 3
	cfg := make_config(t, servers, false)
	defer cfg.cleanup()

	fmt.Printf("Test: agreement despite follower failure ...\n")

	cfg.one(101, servers)

	// follower network failure
	leader := cfg.checkOneLeader()
	cfg.disconnect((leader + 1) % servers)

	// agree despite one failed server?
	cfg.one(102, servers-1)
	cfg.one(103, servers-1)
	time.Sleep(RaftElectionTimeout)
	cfg.one(104, servers-1)
	cfg.one(105, servers-1)

	// failed server re-connected
	cfg.connect((leader + 1) % servers)

	// agree with full set of servers?
	cfg.one(106, servers)
	time.Sleep(RaftElectionTimeout)
	cfg.one(107, servers)

	fmt.Printf("  ... Passed\n")
}

func TestFailNoAgree(t *testing.T) {
	servers := 5
	cfg := make_config(t, servers, false)
	defer cfg.cleanup()

	fmt.Printf("Test: no agreement if too many followers fail ...\n")

	cfg.one(10, servers)

	// 3 of 5 followers disconnect
	leader := cfg.checkOneLeader()
	cfg.disconnect((leader + 1) % servers)
	cfg.disconnect((leader + 2) % servers)
	cfg.disconnect((leader + 3) % servers)

	index, _, ok := cfg.rafts[leader].Start(20)
	if ok != true {
		t.Fatalf("leader rejected Start()")
	}
	if index != 2 {
		t.Fatalf("expected index 2, got %v", index)
	}

	time.Sleep(2 * RaftElectionTimeout)

	n, _ := cfg.nCommitted(index)
	if n > 0 {
		t.Fatalf("%v committed but no majority", n)
	}

	// repair failures
	cfg.connect((leader + 1) % servers)
	cfg.connect((leader + 2) % servers)
	cfg.connect((leader + 3) % servers)

	// the disconnected majority may have chosen a leader from
	// among their own ranks, forgetting index 2.
	// or perhaps
	leader2 := cfg.checkOneLeader()
	index2, _, ok2 := cfg.rafts[leader2].Start(30)
	if ok2 == false {
		t.Fatalf("leader2 rejected Start()")
	}
	if index2 < 2 || index2 > 3 {
		t.Fatalf("unexpected index %v", index2)
	}

	cfg.one(1000, servers)

	fmt.Printf("  ... Passed\n")
}

func TestConcurrentStarts(t *testing.T) {
	servers := 3
	cfg := make_config(t, servers, false)
	defer cfg.cleanup()

	fmt.Printf("Test: concurrent Start()s ...\n")

	var success bool
loop:
	for try := 0; try < 5; try++ {
		if try > 0 {
			// give solution some time to settle
			time.Sleep(3 * time.Second)
		}

		leader := cfg.checkOneLeader()
		_, term, ok := cfg.rafts[leader].Start(1)
		if !ok {
			// leader moved on really quickly
			continue
		}

		iters := 5
		var wg sync.WaitGroup
		is := make(chan int, iters)
		for ii := 0; ii < iters; ii++ {
			wg.Add(1)
			go func(i int) {
				defer wg.Done()
				i, term1, ok := cfg.rafts[leader].Start(100 + i)
				if term1 != term {
					return
				}
				if ok != true {
					return
				}
				is <- i
			}(ii)
		}

		wg.Wait()
		close(is)

		for j := 0; j < servers; j++ {
			if t, _ := cfg.rafts[j].GetState(); t != term {
				// term changed -- can't expect low RPC counts
				continue loop
			}
		}

		failed := false
		cmds := []int{}
		for index := range is {
			cmd := cfg.wait(index, servers, term)
			if ix, ok := cmd.(int); ok {
				if ix == -1 {
					// peers have moved on to later terms
					// so we can't expect all Start()s to
					// have succeeded
					failed = true
					break
				}
				cmds = append(cmds, ix)
			} else {
				t.Fatalf("value %v is not an int", cmd)
			}
		}

		if failed {
			// avoid leaking goroutines
			go func() {
				for range is {
				}
			}()
			continue
		}

		for ii := 0; ii < iters; ii++ {
			x := 100 + ii
			ok := false
			for j := 0; j < len(cmds); j++ {
				if cmds[j] == x {
					ok = true
				}
			}
			if ok == false {
				t.Fatalf("cmd %v missing in %v", x, cmds)
			}
		}

		success = true
		break
	}

	if !success {
		t.Fatalf("term changed too often")
	}

	fmt.Printf("  ... Passed\n")
}

func TestRejoin(t *testing.T) {
	servers := 3
	cfg := make_config(t, servers, false)
	defer cfg.cleanup()

	fmt.Printf("Test: rejoin of partitioned leader ...\n")

	cfg.one(101, servers)

	// leader network failure
	leader1 := cfg.checkOneLeader()
	cfg.disconnect(leader1)

	// make old leader try to agree on some entries
	cfg.rafts[leader1].Start(102)
	cfg.rafts[leader1].Start(103)
	cfg.rafts[leader1].Start(104)

	// new leader commits, also for index=2
	cfg.one(103, 2)

	// new leader network failure
	leader2 := cfg.checkOneLeader()
	cfg.disconnect(leader2)

	// old leader connected again
	cfg.connect(leader1)

	cfg.one(104, 2)

	// all together now
	cfg.connect(leader2)

	cfg.one(105, servers)

	fmt.Printf("  ... Passed\n")
}

func TestBackup(t *testing.T) {
	servers := 5
	cfg := make_config(t, servers, false)
	defer cfg.cleanup()

	fmt.Printf("Test: leader backs up quickly over incorrect follower logs ...\n")

	cfg.one(rand.Int(), servers)

	// put leader and one follower in a partition
	leader1 := cfg.checkOneLeader()
	cfg.disconnect((leader1 + 2) % servers)
	cfg.disconnect((leader1 + 3) % servers)
	cfg.disconnect((leader1 + 4) % servers)

	// submit lots of commands that won't commit
	for i := 0; i < 50; i++ {
		cfg.rafts[leader1].Start(rand.Int())
	}

	time.Sleep(RaftElectionTimeout / 2)

	cfg.disconnect((leader1 + 0) % servers)
	cfg.disconnect((leader1 + 1) % servers)

	// allow other partition to recover
	cfg.connect((leader1 + 2) % servers)
	cfg.connect((leader1 + 3) % servers)
	cfg.connect((leader1 + 4) % servers)

	// lots of successful commands to new group.
	for i := 0; i < 50; i++ {
		cfg.one(rand.Int(), 3)
	}

	// now another partitioned leader and one follower
	leader2 := cfg.checkOneLeader()
	other := (leader1 + 2) % servers
	if leader2 == other {
		other = (leader2 + 1) % servers
	}
	cfg.disconnect(other)

	// lots more commands that won't commit
	for i := 0; i < 50; i++ {
		cfg.rafts[leader2].Start(rand.Int())
	}

	time.Sleep(RaftElectionTimeout / 2)

	// bring original leader back to life,
	for i := 0; i < servers; i++ {
		cfg.disconnect(i)
	}
	cfg.connect((leader1 + 0) % servers)
	cfg.connect((leader1 + 1) % servers)
	cfg.connect(other)

	// lots of successful commands to new group.
	for i := 0; i < 50; i++ {
		cfg.one(rand.Int(), 3)
	}

	// now everyone
	for i := 0; i < servers; i++ {
		cfg.connect(i)
	}
	cfg.one(rand.Int(), servers)

	fmt.Printf("  ... Passed\n")
}

func TestCount(t *testing.T) {
	servers := 3
	cfg := make_config(t, servers, false)
	defer cfg.cleanup()

	fmt.Printf("Test: RPC counts aren't too high ...\n")

	rpcs := func() (n int) {
		for j := 0; j < servers; j++ {
			n += cfg.rpcCount(j)
		}
		return
	}

	leader := cfg.checkOneLeader()

	total1 := rpcs()

	if total1 > 30 || total1 < 1 {
		t.Fatalf("too many or few RPCs (%v) to elect initial leader\n", total1)
	}

	var total2 int
	var success bool
loop:
	for try := 0; try < 5; try++ {
		if try > 0 {
			// give solution some time to settle
			time.Sleep(3 * time.Second)
		}

		leader = cfg.checkOneLeader()
		total1 = rpcs()

		iters := 10
		starti, term, ok := cfg.rafts[leader].Start(1)
		if !ok {
			// leader moved on really quickly
			continue
		}
		cmds := []int{}
		for i := 1; i < iters+2; i++ {
			x := int(rand.Int31())
			cmds = append(cmds, x)
			index1, term1, ok := cfg.rafts[leader].Start(x)
			if term1 != term {
				// Term changed while starting
				continue loop
			}
			if !ok {
				// No longer the leader, so term has changed
				continue loop
			}
			if starti+i != index1 {
				t.Fatalf("Start() failed")
			}
		}

		for i := 1; i < iters+1; i++ {
			cmd := cfg.wait(starti+i, servers, term)
			if ix, ok := cmd.(int); ok == false || ix != cmds[i-1] {
				if ix == -1 {
					// term changed -- try again
					continue loop
				}
				t.Fatalf("wrong value %v committed for index %v; expected %v\n", cmd, starti+i, cmds)
			}
		}

		failed := false
		total2 = 0
		for j := 0; j < servers; j++ {
			if t, _ := cfg.rafts[j].GetState(); t != term {
				// term changed -- can't expect low RPC counts
				// need to keep going to update total2
				failed = true
			}
			total2 += cfg.rpcCount(j)
		}

		if failed {
			continue loop
		}

		if total2-total1 > (iters+1+3)*3 {
			t.Fatalf("too many RPCs (%v) for %v entries\n", total2-total1, iters)
		}

		success = true
		break
	}

	if !success {
		t.Fatalf("term changed too often")
	}

	time.Sleep(RaftElectionTimeout)

	total3 := 0
	for j := 0; j < servers; j++ {
		total3 += cfg.rpcCount(j)
	}

	if total3-total2 > 3*20 {
		t.Fatalf("too many RPCs (%v) for 1 second of idleness\n", total3-total2)
	}

	fmt.Printf("  ... Passed\n")
}

func TestPersist1(t *testing.T) {
	servers := 3
	cfg := make_config(t, servers, false)
	defer cfg.cleanup()

	fmt.Printf("Test: basic persistence ...\n")

	cfg.one(11, servers)

	// crash and re-start all
	for i := 0; i < servers; i++ {
		cfg.start1(i)
	}
	for i := 0; i < servers; i++ {
		cfg.disconnect(i)
		cfg.connect(i)
	}

	cfg.one(12, servers)

	leader1 := cfg.checkOneLeader()
	cfg.disconnect(leader1)
	cfg.start1(leader1)
	cfg.connect(leader1)

	cfg.one(13, servers)

	leader2 := cfg.checkOneLeader()
	cfg.disconnect(leader2)
	cfg.one(14, servers-1)
	cfg.start1(leader2)
	cfg.connect(leader2)

	cfg.wait(4, servers, -1) // wait for leader2 to join before killing i3

	i3 := (cfg.checkOneLeader() + 1) % servers
	cfg.disconnect(i3)
	cfg.one(15, servers-1)
	cfg.start1(i3)
	cfg.connect(i3)

	cfg.one(16, servers)

	fmt.Printf("  ... Passed\n")
}

func TestPersist2(t *testing.T) {
	servers := 5
	cfg := make_config(t, servers, false)
	defer cfg.cleanup()

	fmt.Printf("Test: more persistence ...\n")

	index := 1
	for iters := 0; iters < 5; iters++ {
		cfg.one(10+index, servers)
		index++

		leader1 := cfg.checkOneLeader()

		cfg.disconnect((leader1 + 1) % servers)
		cfg.disconnect((leader1 + 2) % servers)

		cfg.one(10+index, servers-2)
		index++

		cfg.disconnect((leader1 + 0) % servers)
		cfg.disconnect((leader1 + 3) % servers)
		cfg.disconnect((leader1 + 4) % servers)

		cfg.start1((leader1 + 1) % servers)
		cfg.start1((leader1 + 2) % servers)
		cfg.connect((leader1 + 1) % servers)
		cfg.connect((leader1 + 2) % servers)

		time.Sleep(RaftElectionTimeout)

		cfg.start1((leader1 + 3) % servers)
		cfg.connect((leader1 + 3) % servers)

		cfg.one(10+index, servers-2)
		index++

		cfg.connect((leader1 + 4) % servers)
		cfg.connect((leader1 + 0) % servers)
	}

	cfg.one(1000, servers)

	fmt.Printf("  ... Passed\n")
}

func TestPersist3(t *testing.T) {
	servers := 3
	cfg := make_config(t, servers, false)
	defer cfg.cleanup()

	fmt.Printf("Test: partitioned leader and one follower crash, leader restarts ...\n")

	cfg.one(101, 3)

	leader := cfg.checkOneLeader()
	cfg.disconnect((leader + 2) % servers)

	cfg.one(102, 2)

	cfg.crash1((leader + 0) % servers)
	cfg.crash1((leader + 1) % servers)
	cfg.connect((leader + 2) % servers)
	cfg.start1((leader + 0) % servers)
	cfg.connect((leader + 0) % servers)

	cfg.one(103, 2)

	cfg.start1((leader + 1) % servers)
	cfg.connect((leader + 1) % servers)

	cfg.one(104, servers)

	fmt.Printf("  ... Passed\n")
}

//
// Test the scenarios described in Figure 8 of the extended Raft paper. Each
// iteration asks a leader, if there is one, to insert a command in the Raft
// log.  If there is a leader, that leader will fail quickly with a high
// probability (perhaps without committing the command), or crash after a while
// with low probability (most likey committing the command).  If the number of
// alive servers isn't enough to form a majority, perhaps start a new server.
// The leader in a new term may try to finish replicating log entries that
// haven't been committed yet.
//
func TestFigure8(t *testing.T) {
	servers := 5
	cfg := make_config(t, servers, false)
	defer cfg.cleanup()

	fmt.Printf("Test: Figure 8 ...\n")

	cfg.one(rand.Int(), 1)

	nup := servers
	for iters := 0; iters < 1000; iters++ {
		leader := -1
		for i := 0; i < servers; i++ {
			if cfg.rafts[i] != nil {
				_, _, ok := cfg.rafts[i].Start(rand.Int())
				if ok {
					leader = i
				}
			}
		}

		if (rand.Int() % 1000) < 100 {
			ms := rand.Int63() % (int64(RaftElectionTimeout/time.Millisecond) / 2)
			time.Sleep(time.Duration(ms) * time.Millisecond)
		} else {
			ms := (rand.Int63() % 13)
			time.Sleep(time.Duration(ms) * time.Millisecond)
		}

		if leader != -1 {
			cfg.crash1(leader)
			nup -= 1
		}

		if nup < 3 {
			s := rand.Int() % servers
			if cfg.rafts[s] == nil {
				cfg.start1(s)
				cfg.connect(s)
				nup += 1
			}
		}
	}

	for i := 0; i < servers; i++ {
		if cfg.rafts[i] == nil {
			cfg.start1(i)
			cfg.connect(i)
		}
	}

	cfg.one(rand.Int(), servers)

	fmt.Printf("  ... Passed\n")
}

